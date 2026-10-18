#!/bin/sh
# =============================================================================
# Wrapper terraform: ambil API token Proxmox dari macOS Keychain
# Pemakaian: ./tf.sh init | plan | apply | output ...
# Token dibuat/diperbarui oleh: ansible-playbook playbooks/setup-terraform-access.yml
# =============================================================================
set -eu
cd "$(dirname "$0")"

ACCOUNT='terraform@pve!iac'
SECRET=$(security find-generic-password -a "$ACCOUNT" -s proxmoxmqr-home-terraform -w 2>/dev/null) || {
    echo "Token Terraform tidak ada di Keychain." >&2
    echo "Jalankan dulu: ansible-playbook playbooks/setup-terraform-access.yml" >&2
    exit 1
}

PROXMOX_VE_API_TOKEN="${ACCOUNT}=${SECRET}" exec terraform "$@"
