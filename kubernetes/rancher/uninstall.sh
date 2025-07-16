#/bin/sh
# Rancher
helm uninstall rancher --namespace cattle-system

# Cert Manager
sh ../cert-manager/uninstall.sh
