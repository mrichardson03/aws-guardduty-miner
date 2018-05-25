#!/bin/sh

cd /opt/minemeld/local/library/gd/
sudo -u minemeld -H /opt/minemeld/engine/current/bin/pip install aws_guardduty_miner*.whl
sudo service minemeld restart