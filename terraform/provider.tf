# Kredensial TIDAK ditulis di sini. tf.sh mengisi environment variable:
#   PROXMOX_VE_API_TOKEN = terraform@pve!iac=<secret dari Keychain>
# Token dibuat oleh Ansible: playbooks/setup-terraform-access.yml
provider "proxmox" {
  endpoint = var.proxmox_endpoint
  insecure = true # sertifikat self-signed bawaan Proxmox
}
