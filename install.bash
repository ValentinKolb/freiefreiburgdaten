#!/usr/bin/env bash

# This script installs freiefreiburgdaten and sets up the systemd unit file
# Author:  Valentin Kolb
# Version: 1.5
# License: MIT

set -e
set -o pipefail

sudo mkdir -p /var/lib/fff
sudo git clone https://github.com/ValentinKolb/freiefreiburgdaten.git /var/lib/fff
sudo ln -s /var/lib/fff/src/fff.service /lib/systemd/system/fff.service
sudo pip3.9 install -r /var/lib/fff/requirements.txt

echo "Run 'sudo systemctl start fff' to start the server on port 8050"