# TODO

Pekerjaan lanjutan, diurutkan dari dampak terbesar terhadap keamanan & ketahanan.

## Keamanan

- [ ] **PostgreSQL TLS dengan CA homelab** — ganti sertifikat snakeoil bawaan Ubuntu
      memakai role `tls_cert`; klien aplikasi pakai `sslmode=verify-full`.
- [ ] **Batasi firewall host Proxmox** — aturan datacenter masih membuka SSH & 8006
      untuk semua sumber; batasi ke IPSet admin (rencanakan jalur darurat dulu).
- [ ] **Cloudflare Access** di depan Web UI Proxmox (verifikasi email sebelum halaman login).
- [ ] **Batasi lalu lintas keluar (egress)** dari LXC — proxy untuk apt/Docker/SMTP.
- [ ] **TLS + autentikasi untuk Grafana/Prometheus/Loki** (saat ini HTTP di LAN,
      dibatasi firewall & `DOCKER-USER`).
- [ ] **Client ID Google Drive sendiri dengan scope `drive.file`** — client ID bawaan
      rclone dipensiunkan 2026, dan token saat ini punya akses ke seluruh Drive.
- [ ] Rotasi berkala secret (password DB, Redis, replikasi) + runbook rotasi.
- [ ] Reservasi DHCP untuk perangkat admin (IPSet `hl-admin`).

## Ketersediaan & DR

- [ ] **Failover otomatis** (Patroni + etcd, butuh node witness ketiga) — saat ini
      failover satu perintah, dimulai manual.
- [ ] **Sinkronisasi upload pengguna real-time** ke standby (saat ini ikut saat deploy)
      atau pindah ke object storage.
- [ ] Failover aplikasi otomatis (health-check di Cloudflare / load balancer).
- [ ] Jadwalkan `pitr-drill.yml` rutin (bulanan) + alert jika gagal.
- [ ] Selidiki upload offsite lambat (data terkirim ±5× ukuran file; uji `--drive-chunk-size`, log `-vv`).
- [ ] Pindahkan Laravel cache/session/queue ke Redis (TLS) setelah CA dipasang di host aplikasi.

## Jaringan

- [ ] VLAN 802.1Q sungguhan (butuh switch/router managed) atau SDN Proxmox per tier
      dengan subnet terpisah — saat ini mikrosegmentasi firewall di satu subnet.

## Kualitas kode & operasional

- [ ] CI: `ansible-lint`, `yamllint`, `terraform fmt/validate`, secret scanning (gitleaks).
- [ ] Hapus komponen yang tidak dipakai: role `backup_agent`, template
      `otel-collector.yml.j2`, variabel aplikasi DKM/DEV di `group_vars`.
- [ ] Kunci versi Grafana Alloy native (saat ini mengikuti repo apt).
- [ ] Upgrade Grafana ke 11.x (dashboard Node Exporter Full terbaru butuh ≥ 11.6).
- [ ] Monitoring repo apt yang gagal (`download.proxmox.com` sempat tak terjangkau).
- [ ] Tambahkan lisensi repo.
