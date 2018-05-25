import logging
import os
import shutil
import yaml

import boto3
import jmespath

from minemeld.ft.basepoller import BasePollerFT

LOG = logging.getLogger(__name__)


class GuardDutyMiner(BasePollerFT):

    def configure(self):
        super(GuardDutyMiner, self).configure()

        self.aws_access_key_id = self.config.get('aws_access_key_id')
        self.aws_secret_access_key = self.config.get('aws_secret_access_key')
        self.region_name = self.config.get('region_name')
        self.detector_id = self.config.get('detector_id')
        self.verify_cert = self.config.get('verify_cert', True)

        self.side_config_path = self.config.get('side_config', None)
        if self.side_config_path is None:
            self.side_config_path = os.path.join(
                os.environ['MM_CONFIG_DIR'],
                '%s_side_config.yml' % self.name
            )

        self.client = None

        self._load_side_config()

        try:
            self.client = boto3.client(
                'guardduty', region_name=self.region_name, verify=self.verify_cert,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        except Exception as e:
            LOG.error('%s - Boto3 exception: %s', self.name, str(e))
            return

    def _load_side_config(self):
        try:
            with open(self.side_config_path, 'r') as f:
                sconfig = yaml.safe_load(f)

        except Exception as e:
            LOG.error('%s - Error loading side config: %s', self.name, str(e))
            return

        self.aws_access_key_id = sconfig.get('aws_access_key_id')
        if self.aws_access_key_id is not None:
            LOG.info('%s - access key set', self.name)

        self.aws_secret_access_key = sconfig.get('aws_secret_access_key')
        if self.aws_secret_access_key is not None:
            LOG.info('%s - secret access key set', self.name)

        self.region_name = sconfig.get('region_name')
        if self.region_name is not None:
            LOG.info('%s - region name set', self.region_name)

        self.detector_id = sconfig.get('detector_id')
        if self.detector_id is not None:
            LOG.info('%s - detector id set', self.name)

    def _build_iterator(self, item):
        if not self.client:
            LOG.error('%s - error loading boto3 client', self.name)
            return

        not_archived = {'Criterion': {'service.archived': {'Eq': ['false']}}}
        finding_ids = self.client.list_findings(
            DetectorId=self.detector_id, FindingCriteria=not_archived
        )['FindingIds']
        LOG.info('%s - finding ids: %s', self.name, finding_ids)

        return self.client.get_findings(
            DetectorId=self.detector_id, FindingIds=finding_ids
        )['Findings']

    def _process_item(self, item):
        LOG.info('%s - processing finding: %s', self.name, item['Id'])

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
        super(GuardDutyMiner, self).hup(source=source)

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
