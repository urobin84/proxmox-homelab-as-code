# =============================================================================
# Terraform - lapis VIRTUAL (definisi LXC di Proxmox node pve)
#   Lapis fisik (host pve) & software (isi LXC) dikelola Ansible di folder induk
#   Jalankan lewat ./tf.sh (mengambil API token dari macOS Keychain)
# =============================================================================
terraform {
  required_version = ">= 1.7.0" # import block dengan for_each

  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.115.0"
    }
  }
}
