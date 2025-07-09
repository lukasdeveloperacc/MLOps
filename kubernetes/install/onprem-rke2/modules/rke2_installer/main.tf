resource "null_resource" "install_rke2_local" {
  count = var.is_local ? 1 : 0

  provisioner "local-exec" {
    command = <<EOT
      curl -sfL https://get.rke2.io | sudo sh -
      sudo systemctl enable rke2-server.service
      sudo systemctl start rke2-server.service
    EOT
  }
}


resource "null_resource" "install_rke2_remote" {
    count = var.is_local && var.private_key_path == "" ? 0 : 1

    connection {
        type        = "ssh"
        host        = var.host_ip
        user        = var.ssh_user
        private_key = file(var.private_key_path)
    }

    provisioner "remote-exec" {
        inline = [
            "curl -sfL https://get.rke2.io | sudo sh -",
            "sudo systemctl enable rke2-server.service",
            "sudo systemctl start rke2-server.service"
        ]
    }
}
