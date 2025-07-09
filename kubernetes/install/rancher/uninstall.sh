#/bin/sh
# Rancher
helm uninstall rancher --namespace cattle-system

# Cert Manager
helm uninstall cert-manager --namespace cert-manager
kubectl delete namespace cattle-system
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.18.2/cert-manager.crds.yaml
