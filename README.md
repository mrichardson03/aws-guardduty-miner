# aws-guardduty-miner
MineMeld Miner for [AWS GuardDuty](https://aws.amazon.com/guardduty/) implemented as an extension.

## Requirements

This extension requires MineMeld to be running on Ubuntu 16.04, which is currently marked as 
**EXPERIMENTAL**.  Running on Ubuntu 14.04 results in an OpenSSL version that is too old to
successfully talk to GuardDuty.  To deploy on the required version, use the 
[minemeld-ansible](https://github.com/PaloAltoNetworks/minemeld-ansible) playbook.

## Installation

You can install this extension directly from the git repository using the MineMeld GUI, or build 
the python wheel with: `python setup.py bdist_wheel` and install as an extension.

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