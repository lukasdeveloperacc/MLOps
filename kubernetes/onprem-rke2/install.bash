#/bin/bash

# Version : https://github.com/rancher/rke2/releases
curl -sfL https://get.rke2.io --output rke2_install.sh
chmod +x ./rke2_install.sh
INSTALL_RKE2_CHANNEL=v1.35.0+rke2r1 ./rke2_install.sh

systemctl enable rke2-server.service
systemctl start rke2-server.service

rm -rf ./rke2_install.sh
