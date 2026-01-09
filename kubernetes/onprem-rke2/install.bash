#/bin/bash

# Version : https://github.com/rancher/rke2/releases
curl -sfL https://get.rke2.io | INSTALL_RKE2_VERSION=v1.35.0+rke2r1 sh -
systemctl enable rke2-server.service
systemctl start rke2-server.service
