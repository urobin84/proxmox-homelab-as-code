# =============================================================================
# Import LXC yang sudah berjalan (dibuat manual sebelum ada Terraform).
# Setelah "terraform apply" pertama sukses, blok ini boleh tetap ada (no-op)
# atau dihapus. LXC baru cukup ditambahkan di terraform.tfvars tanpa import.
# =============================================================================
import {
  for_each = toset(["101", "102", "103", "104", "105", "106"])
  to       = proxmox_virtual_environment_container.lxc[each.key]
  id       = "${var.node_name}/${each.key}"
}
