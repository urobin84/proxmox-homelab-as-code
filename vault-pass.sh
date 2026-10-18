#!/bin/sh
# =============================================================================
# Ambil password Ansible Vault dari macOS Keychain (dipakai ansible.cfg)
# Password TIDAK disimpan di file ini.
#
# Simpan password sekali (akan diminta mengetik password, tidak tampil):
#   security add-generic-password -a ansible-vault -s proxmoxmqr-home -w
# Ganti password tersimpan:
#   security add-generic-password -U -a ansible-vault -s proxmoxmqr-home -w
# =============================================================================
exec security find-generic-password -a ansible-vault -s proxmoxmqr-home -w
