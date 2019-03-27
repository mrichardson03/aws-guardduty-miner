# aws-guardduty-miner

[![Build Status](https://travis-ci.org/mrichardson03/aws-guardduty-miner.svg?branch=master)](https://travis-ci.org/mrichardson03/aws-guardduty-miner)

MineMeld Miner for [AWS GuardDuty](https://aws.amazon.com/guardduty/) implemented as an extension.

## Installation

You can install this extension directly from the git repository using the
MineMeld GUI:

After installing, restart the MineMeld services:

```
sudo -u minemeld /opt/minemeld/engine/current/bin/supervisorctl -c /opt/minemeld/local/supervisor/config/supervisord.conf restart all
```

Now, clone a new `guardduty.miner` node, and commit the configuration.  You may
need to refresh your browser manually to see the prototype.

Finally, edit the cloned node's properties, and add the AWS region, access key,
secret key, and GuardDuty collector ID.

## Usage

The miner processes the following active (i.e., *not archived*) GuardDuty findings for inbound and 
outbound IPv4 indicators.  All indicators are currently outputted with a 100 confidence rating, so 
use appropriately.  Once a finding is archived in the GuardDuty console, corresponding indicators
will be aged out of the feeds.

**Inbound**
- UnauthorizedAccess:EC2/TorIPCaller
- UnauthorizedAccess:EC2/MaliciousIPCaller.Custom
- UnauthorizedAccess:EC2/SSHBruteForce
- UnauthorizedAccess:EC2/RDPBruteForce
- Recon:EC2/PortProbeUnprotectedPort

**Outbound**
- Backdoor:EC2/XORDDOS
- Backdoor:EC2/Spambot
- Behavior:EC2/NetworkPortUnusual
- Behavior:EC2/TrafficVolumeUnusual
- Trojan:EC2/BlackholeTraffic
- Trojan:EC2/DropPoint
- Recon:EC2/Portscan