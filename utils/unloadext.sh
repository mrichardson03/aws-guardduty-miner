#!/bin/sh

sudo -u minemeld -H /opt/minemeld/engine/current/bin/pip uninstall aws-guardduty-miner
sudo service minemeld restart
