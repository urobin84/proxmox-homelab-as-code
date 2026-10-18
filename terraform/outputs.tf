output "containers" {
  description = "Ringkasan LXC (VMID → hostname, IP, role)"
  value = {
    for id, c in local.lxc : id => {
      hostname = c.hostname
      ip       = c.ip
      role     = c.role
    }
  }
}

# Potongan siap tempel untuk ../inventory.ini - pastikan sama dengan inventory Ansible
output "ansible_inventory_hosts" {
  description = "Baris host untuk inventory Ansible"
  value = join("\n", [
    for id, c in local.lxc : "${c.hostname} ansible_host=${c.ip} lxc_id=${id}  # ${c.role}"
  ])
}
