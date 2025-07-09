# Overview
- **IaC (Infra as Code)**

# Install Terraform
- [Installation Docs](https://developer.hashicorp.com/terraform/install#linux)

# Install RKE2
## On-prem
```bash
cd install/onprem
```
- Locally
  ```bash
  terraform plan -var="is_local=true"
  ```
- Remote
  ```bash
  terraform plan -var="is_local=false" -var="host_ip=" -var="ssh_user=" -var="private_key_path="
  ```
