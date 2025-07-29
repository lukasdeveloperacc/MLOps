# Overview
- **IaC (Infra as Code)**

# Install Terraform
- [Installation Docs](https://developer.hashicorp.com/terraform/install#linux)

# Kubeflow
## On-prem
```bash
sh onprem-rke2/install.sh
sh tools/kubectl/install.sh
sh tools/helm/install.sh
sh cert-manager/install.sh
sh rancher/install.sh
sh persistent_volume/local_path_provisioner/install.sh
sh kubeflow/pipelines/install.sh
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
