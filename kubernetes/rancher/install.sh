#/bin/sh

# [Ref] https://ranchermanager.docs.rancher.com/getting-started/quick-start-guides/deploy-rancher-manager/helm-cli

# Cert Manager
sh ../cert-manager/install.sh

# Rancher
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
kubectl create namespace cattle-system

IP="172.30.1.149"
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname="${IP}.sslip.io" \
  --set replicas=1 \
  --set bootstrapPassword="abc1234" \
  --create-namespace \
  --install
