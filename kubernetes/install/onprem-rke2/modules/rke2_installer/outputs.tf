output "rke2_installed" {
    value = var.is_local ? "RKE2 installed locally" : "RKE2 installed remotely on ${var.host_ip}"
}
