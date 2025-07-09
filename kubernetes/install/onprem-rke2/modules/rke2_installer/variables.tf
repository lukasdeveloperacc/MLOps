variable "is_local" {
  description = "Installation in local or not"
  type        = bool
  default     = true
}

variable "host_ip" {
    description = "Public IP or Domain of the target host. You can use it when you apply is_local to be true"
    type = string
    default = "172.188.1.56"
}

variable "ssh_user" {
  type        = string
  description = "On the Remote case, you can set ssh user"
  default     = "azureuser"
}

variable "private_key_path" {
  type        = string
  description = "On the Remote case, you can set ssh private key path"
  default     = "~/.ssh/id_rsa"
}
