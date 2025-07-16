#/bin/sh

# [Ref] https://ranchermanager.docs.rancher.com/getting-started/quick-start-guides/deploy-rancher-manager/helm-cli

# Cert Manager
sh ../cert-manager/install.sh

# Rancher
IP="172.188.1.56"
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname="${IP}.sslip.io" \
  --set replicas=1 \
  --set bootstrapPassword="abc1234" \
  --create-namespace \
  --install
