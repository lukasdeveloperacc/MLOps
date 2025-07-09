module "rke2_installer" {
    source = "./modules/rke2_installer"
    is_local = var.is_local
    host_ip = var.host_ip
    ssh_user = var.ssh_user
    private_key_path = var.private_key_path
}
