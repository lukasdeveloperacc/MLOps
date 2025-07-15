#/bin/sh

# [Ref] https://ranchermanager.docs.rancher.com/getting-started/quick-start-guides/deploy-rancher-manager/helm-cli

# Cert Manager
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
kubectl create namespace cattle-system
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.18.2/cert-manager.crds.yaml

helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --install

# Rancher
IP="172.188.1.56"
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname="${IP}.sslip.io" \
  --set replicas=1 \
  --set bootstrapPassword="abc1234" \
  --create-namespace \
  --install
