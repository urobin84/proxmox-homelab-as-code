# =============================================================================
# LXC containers - semua dari var.containers (terraform.tfvars)
# =============================================================================
locals {
  lxc = {
    for id, c in var.containers : id => merge(c, {
      cores       = coalesce(c.cores, var.lxc_defaults.cores)
      memory_mb   = coalesce(c.memory_mb, var.lxc_defaults.memory_mb)
      swap_mb     = coalesce(c.swap_mb, var.lxc_defaults.swap_mb)
      disk_gb     = coalesce(c.disk_gb, var.lxc_defaults.disk_gb)
      nameservers = coalesce(c.nameservers, var.lxc_defaults.nameservers)
    })
  }
}

resource "proxmox_virtual_environment_container" "lxc" {
  for_each = local.lxc

  node_name     = var.node_name
  vm_id         = tonumber(each.key)
  unprivileged  = true
  start_on_boot = true
  started       = true

  features {
    nesting = true # dibutuhkan Docker (LXC 101/106) & systemd modern
  }

  # Default Proxmox - ditulis eksplisit agar tidak terlihat sebagai perubahan
  console {
    enabled   = true
    tty_count = 2
    type      = "tty"
  }

  cpu {
    cores = each.value.cores
  }

  memory {
    dedicated = each.value.memory_mb
    swap      = each.value.swap_mb
  }

  disk {
    datastore_id = var.lxc_defaults.datastore
    size         = each.value.disk_gb
  }

  # Urutan boot: repo backup/monitoring → database → Redis → aplikasi (lihat tfvars)
  dynamic "startup" {
    for_each = each.value.startup_order == null ? [] : [1]
    content {
      order    = each.value.startup_order
      up_delay = each.value.startup_up_delay
    }
  }

  # PERHATIAN: provider bpg menganggap TAMBAH/UBAH mount_point = buat ulang
  # container (forces replacement) - ditolak prevent_destroy. Untuk LXC yang
  # sudah ada: tambahkan di tfvars, lalu di host pve jalankan
  #   pct set <id> --mpN local-lvm:<GB>,mp=<path>,backup=1   (hot-add, tanpa reboot)
  # dan pastikan "./tf.sh plan" → No changes.
  dynamic "mount_point" {
    for_each = each.value.mount_points
    content {
      volume = var.lxc_defaults.datastore
      size   = "${mount_point.value.size_gb}G"
      path   = mount_point.value.path
      backup = mount_point.value.backup
    }
  }

  network_interface {
    name        = "eth0"
    bridge      = var.network.bridge
    mac_address = each.value.mac_address
    # Mikrosegmentasi firewall Proxmox (aturan: Ansible role proxmox_firewall).
    # JANGAN di-false-kan: semua LXC kehilangan isolasi antar-server.
    firewall = true
  }

  # PERHATIAN: mengubah hostname/dns/ip lewat "apply" membuat provider
  # me-REBOOT LXC yang sedang jalan (~10 detik) agar file di dalam LXC ikut
  # diperbarui. Untuk LXC produksi tanpa downtime: ubah nilainya di
  # terraform.tfvars, lalu di host pve jalankan "pct set <id> --searchdomain ..
  # --nameserver .." + tulis /etc/resolv.conf di dalam LXC; "plan" → No changes.
  initialization {
    hostname = each.value.hostname

    dns {
      domain  = var.lxc_defaults.searchdomain
      servers = each.value.nameservers
    }

    ip_config {
      ipv4 {
        address = "${each.value.ip}/${var.network.cidr_prefix}"
        gateway = var.network.gateway
      }
    }
  }

  operating_system {
    template_file_id = var.lxc_template
    type             = "ubuntu"
  }

  lifecycle {
    # LXC berisi data produksi - hapus dari tfvars TIDAK boleh menghapus container
    prevent_destroy = true

    # Hanya dipakai saat container dibuat; tidak tersimpan di config Proxmox,
    # sehingga setelah import selalu terlihat berbeda
    ignore_changes = [
      operating_system[0].template_file_id,
      initialization[0].user_account,
    ]
  }
}
