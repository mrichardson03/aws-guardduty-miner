import logging
import os
import shutil
import yaml

import boto3
import jmespath

from minemeld.ft.basepoller import BasePollerFT

# we need pyOpenSSL in Python < 2.7.9 to enable SNI and TLS
# as botocore uses its own version of requests/urllib3 we should
# enable pyopenssl there
import botocore.vendored.requests.packages.urllib3.contrib.pyopenssl
botocore.vendored.requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()

LOG = logging.getLogger(__name__)


class Miner(BasePollerFT):
    def __init__(self, name, chassis, config):
        self.client = None

        super(Miner, self).__init__(name, chassis, config)

    def configure(self):
        super(Miner, self).configure()

        self.aws_access_key_id = self.config.get('aws_access_key_id', None)
        self.aws_secret_access_key = self.config.get('aws_secret_access_key', None)
        self.region_name = self.config.get('region_name', None)
        self.detector_id = self.config.get('detector_id', None)
        self.verify_cert = self.config.get('verify_cert', True)

        self.side_config_path = self.config.get('side_config', None)
        if self.side_config_path is None:
            self.side_config_path = os.path.join(
                os.environ['MM_CONFIG_DIR'],
                '%s_side_config.yml' % self.name
            )

        self._load_side_config()

    def _load_side_config(self):
        try:
            with open(self.side_config_path, 'r') as f:
                sconfig = yaml.safe_load(f)

        except Exception as e:
            LOG.error('%s - Error loading side config: %s', self.name, str(e))
            return

        aws_access_key_id = sconfig.get('aws_access_key_id', None)
        if aws_access_key_id is not None:
            self.aws_access_key_id = aws_access_key_id
            LOG.info('%s - access key set', self.name)

        aws_secret_access_key = sconfig.get('aws_secret_access_key', None)
        if aws_secret_access_key is not None:
            self.aws_secret_access_key = aws_secret_access_key
            LOG.info('%s - secret access key set', self.name)

        region_name = sconfig.get('region_name', None)
        if region_name is not None:
            self.region_name = region_name
            LOG.info('%s - region name set', self.region_name)

        detector_id = sconfig.get('detector_id', None)
        if detector_id is not None:
            self.detector_id = detector_id
            LOG.info('%s - detector id set', self.name)

    def _build_iterator(self, item):
        if self.region_name is None:
            raise RuntimeError('{} - Region name not set, poll not performed'.format(self.name))
        if self.aws_access_key_id is None:
            raise RuntimeError(
                '{} - AWS Access Key ID not set, poll not performed'.format(self.name)
            )
        if self.aws_secret_access_key is None:
            raise RuntimeError(
                '{} - AWS Secret Access Key not set, poll not performed'.format(self.name)
            )

        self.client = boto3.client(
            'guardduty', region_name=self.region_name, verify=self.verify_cert,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

        not_archived = {'Criterion': {'service.archived': {'Eq': ['false']}}}
        finding_ids = self.client.list_findings(
            DetectorId=self.detector_id, FindingCriteria=not_archived
        )['FindingIds']
        LOG.debug('%s - finding ids: %s', self.name, finding_ids)

        return self.client.get_findings(
            DetectorId=self.detector_id, FindingIds=finding_ids
        )['Findings']

    def _process_item(self, item):
        LOG.debug('%s - processing finding: %s', self.name, item['Id'])

        if item['Type'] == 'Recon:EC2/PortProbeUnprotectedPort':
            indicators = []

            for ip in jmespath.search(
                'Service.Action.PortProbeAction.PortProbeDetails[].RemoteIpDetails.IpAddressV4',
                item
            ):
                indicators.append(
                    [ip, {'type': 'IPv4', 'confidence': 100, 'direction': 'inbound'}]
                )

            return indicators
        else:
            if jmespath.search('Service.Action.ActionType', item) == 'NETWORK_CONNECTION':
                direction = jmespath.search(
                    'Service.Action.NetworkConnectionAction.ConnectionDirection', item
                )

                if direction:
                    value = {'type': 'IPv4', 'confidence': 100, 'direction': direction.lower()}

                    indicator = jmespath.search(
                        'Service.Action.NetworkConnectionAction.RemoteIpDetails.IpAddressV4',
                        item
                    )

                    return [[indicator, value]]

        return []

    def hup(self, source=None):
        LOG.info('%s - hup received, reload side config')
        self._load_side_config()
        super(Miner, self).hup(source=source)

    @staticmethod
    def gc(name, config=None):
        BasePollerFT.gc(name, config)

        shutil.rmtree('{}_temp'.format(name), ignore_errors=True)
        side_config_path = None
        if config is not None:
            side_config_path = config.get('side_config')
        if side_config_path is None:
            side_config_path = os.path.join(
                os.environ['MM_CONFIG_DIR'],
                '{}_side_config.yml'.format(name)
            )

        try:
            os.remove(side_config_path)
        except Exception:
            pass
