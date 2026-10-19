# Nilai jaringan (endpoint, gateway) sengaja tanpa default - diisi di
# terraform.tfvars (tidak di-commit; contoh: terraform.tfvars.example)
variable "proxmox_endpoint" {
  description = "URL API Proxmox, mis. https://<ip-proxmox>:8006/"
  type        = string
}

variable "node_name" {
  description = "Nama node Proxmox"
  type        = string
  default     = "pve"
}

variable "lxc_template" {
  description = "Template OS untuk LXC baru (LXC yang sudah ada tidak terpengaruh)"
  type        = string
  default     = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
}

variable "ssh_public_key_file" {
  description = "Kunci publik SSH yang dipasang ke root LXC BARU (dipakai Ansible). LXC yang sudah ada tidak terpengaruh"
  type        = string
  default     = "~/.ssh/proxmoxmqr_home.pub"
}

variable "network" {
  description = "Jaringan LAN untuk semua LXC"
  type = object({
    bridge      = string
    cidr_prefix = number
    gateway     = string
  })
}

variable "lxc_defaults" {
  description = "Spesifikasi default LXC (bisa ditimpa per container di var.containers)"
  type = object({
    cores        = number
    memory_mb    = number
    swap_mb      = number
    disk_gb      = number
    datastore    = string
    nameservers  = list(string)
    searchdomain = string
  })
}

variable "containers" {
  description = "LXC yang dikelola Terraform. Key = VMID."
  type = map(object({
    hostname    = string
    ip          = string
    mac_address = optional(string) # kosong = dibuat otomatis oleh Proxmox (LXC baru)
    role        = string
    cores       = optional(number)
    memory_mb   = optional(number)
    swap_mb     = optional(number)
    disk_gb     = optional(number)
    nameservers = optional(list(string))
    # Urutan start saat host boot (kecil = lebih dulu; shutdown = urutan
    # terbalik) & jeda detik sebelum LXC urutan berikutnya distart
    startup_order    = optional(number)
    startup_up_delay = optional(number, 0)
    # Disk tambahan (volume di datastore lxc_defaults.datastore)
    mount_points = optional(list(object({
      path    = string
      size_gb = number
      backup  = optional(bool, true) # ikut vzdump
    })), [])
  }))
}
