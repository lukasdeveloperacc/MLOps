#/bin/sh

kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.18.2/cert-manager.crds.yaml
helm uninstall cert-manager --namespace cert-manager
kubectl delete namespace cattle-system
