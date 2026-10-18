"""Generator dashboard Grafana "Homelab Overview".

Pemakaian (dari root repo):
    python3 tools/gen_homelab_dashboard.py roles/monitoring/files/dashboards/homelab-overview.json
lalu deploy: ansible-playbook playbooks/deploy-monitoring.yml --limit BACKUP-AND-MONITORING
"""
import json
import sys

PROM = {"type": "prometheus", "uid": "prometheus"}
LOKI = {"type": "loki", "uid": "loki"}
panels = []
_id = 0


def nid():
    global _id
    _id += 1
    return _id


def row(title, y):
    panels.append({"type": "row", "id": nid(), "title": title, "collapsed": False,
                   "gridPos": {"h": 1, "w": 24, "x": 0, "y": y}, "panels": []})


def target(expr, legend="", instant=False, ds=PROM, ref="A"):
    t = {"datasource": ds, "expr": expr, "refId": ref}
    if ds is PROM:
        t.update({"legendFormat": legend, "instant": instant, "range": not instant})
    elif legend:
        t["legendFormat"] = legend
    return t


def thresholds(steps):
    return {"mode": "absolute", "steps": [{"color": c, "value": v} for c, v in steps]}


def stat(title, targets, x, y, w, h, unit="none", steps=None, mappings=None, desc="", decimals=None, color_mode="background"):
    defaults = {"unit": unit, "thresholds": thresholds(steps or [("green", None)]),
                "color": {"mode": "thresholds"}, "mappings": mappings or []}
    if decimals is not None:
        defaults["decimals"] = decimals
    panels.append({"type": "stat", "id": nid(), "title": title, "description": desc, "datasource": targets[0]["datasource"],
                   "gridPos": {"h": h, "w": w, "x": x, "y": y}, "targets": targets,
                   "fieldConfig": {"defaults": defaults, "overrides": []},
                   "options": {"colorMode": color_mode, "graphMode": "none", "justifyMode": "center",
                               "textMode": "value_and_name", "orientation": "auto",
                               "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}}})


def bargauge(title, targets, x, y, w, h, unit="percent", steps=None, minv=0, maxv=100, desc=""):
    panels.append({"type": "bargauge", "id": nid(), "title": title, "description": desc, "datasource": PROM,
                   "gridPos": {"h": h, "w": w, "x": x, "y": y}, "targets": targets,
                   "fieldConfig": {"defaults": {"unit": unit, "min": minv, "max": maxv,
                                                "thresholds": thresholds(steps or [("green", None), ("orange", 75), ("red", 90)]),
                                                "color": {"mode": "thresholds"}}, "overrides": []},
                   "options": {"displayMode": "gradient", "orientation": "horizontal", "showUnfilled": True,
                               "valueMode": "color", "namePlacement": "left",
                               "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}}})


def timeseries(title, targets, x, y, w, h, unit="short", ds=PROM, desc="", bars=False):
    custom = {"drawStyle": "bars" if bars else "line", "lineWidth": 1, "fillOpacity": 30 if bars else 10,
              "showPoints": "never", "spanNulls": False, "stacking": {"mode": "normal" if bars else "none"}}
    panels.append({"type": "timeseries", "id": nid(), "title": title, "description": desc, "datasource": ds,
                   "gridPos": {"h": h, "w": w, "x": x, "y": y}, "targets": targets,
                   "fieldConfig": {"defaults": {"unit": unit, "custom": custom, "color": {"mode": "palette-classic"}}, "overrides": []},
                   "options": {"legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                               "tooltip": {"mode": "multi", "sort": "desc"}}})


def logs(title, expr, x, y, w, h, desc=""):
    panels.append({"type": "logs", "id": nid(), "title": title, "description": desc, "datasource": LOKI,
                   "gridPos": {"h": h, "w": w, "x": x, "y": y},
                   "targets": [{"datasource": LOKI, "expr": expr, "refId": "A", "queryType": "range"}],
                   "options": {"showTime": True, "wrapLogMessage": True, "sortOrder": "Descending",
                               "enableLogDetails": True, "dedupStrategy": "none", "prettifyLogMessage": False,
                               "showLabels": False, "showCommonLabels": False}})


UPDOWN = [{"type": "value", "options": {"0": {"text": "DOWN", "color": "red", "index": 0},
                                        "1": {"text": "UP", "color": "green", "index": 1}}}]

# --- Ringkasan host -----------------------------------------------------------
row("Ringkasan", 0)
stat("Host (node exporter)", [target('up{job="node"}', "{{host}}", instant=True)], 0, 1, 24, 3,
     steps=[("red", None), ("green", 1)], mappings=UPDOWN,
     desc="Status scrape node exporter semua LXC & host pve")

# --- Uptime aplikasi ----------------------------------------------------------
row("Uptime aplikasi & service (Blackbox)", 4)
stat("Status probe", [target("probe_success", "{{probe}}", instant=True)], 0, 5, 8, 6,
     steps=[("red", None), ("green", 1)], mappings=UPDOWN,
     desc="Dicek dari LXC 106 setiap 30 detik")
timeseries("Waktu respons", [target("probe_duration_seconds", "{{probe}}")], 8, 5, 16, 6, unit="s")

# --- Alert aktif --------------------------------------------------------------
row("Alert aktif", 11)
panels.append({"type": "table", "id": nid(), "title": "Alert yang sedang FIRING", "datasource": PROM,
               "description": "Sama dengan yang dikirim Alertmanager via email",
               "gridPos": {"h": 6, "w": 24, "x": 0, "y": 12},
               "targets": [target('ALERTS{alertstate="firing"}', instant=True)] ,
               "transformations": [{"id": "labelsToFields", "options": {"mode": "columns"}},
                                   {"id": "organize", "options": {"excludeByName": {"Time": True, "Value": True, "__name__": True, "alertstate": True},
                                                                  "indexByName": {"alertname": 0, "severity": 1, "host": 2}}}],
               "fieldConfig": {"defaults": {"custom": {"align": "auto"}, "noValue": "Tidak ada alert aktif"}, "overrides": []},
               "options": {"showHeader": True, "cellHeight": "sm"}})

# --- Backup -------------------------------------------------------------------
row("Backup", 18)
bargauge("Umur backup vzdump per LXC",
         [target("(time() - (homelab_vzdump_last_backup_timestamp_seconds > 0)) / 3600", "{{vmid}} {{guest}}", instant=True)],
         0, 19, 10, 7, unit="h", minv=0, maxv=48, steps=[("green", None), ("orange", 24), ("red", 26)],
         desc="Jam sejak file backup terbaru di BackupFolder (HDD). Job harian 02:00; merah = > 26 jam")
stat("LXC belum pernah di-backup", [target("count(homelab_vzdump_last_backup_timestamp_seconds == 0) or vector(0)", "LXC", instant=True)],
     10, 19, 4, 3, steps=[("green", None), ("red", 1)])
stat("Offsite GDrive terakhir sukses", [target("(time() - homelab_offsite_last_success_timestamp_seconds) / 86400", "hari lalu", instant=True)],
     14, 19, 5, 3, unit="d", decimals=1, steps=[("green", None), ("orange", 7), ("red", 8)],
     desc="Upload terenkripsi mingguan (Minggu 05:00)")
stat("pg_dump terakhir sukses", [target("(time() - homelab_pg_backup_last_success_timestamp_seconds) / 3600", "jam lalu", instant=True)],
     19, 19, 5, 3, unit="h", decimals=1, steps=[("green", None), ("orange", 25), ("red", 26)],
     desc="Dump harian 01:30 di LXC 104")
bargauge("Ukuran backup terbaru", [target("homelab_vzdump_last_backup_size_bytes > 0", "{{vmid}} {{guest}}", instant=True)],
         10, 22, 14, 4, unit="bytes", minv=0, maxv=None, steps=[("blue", None)])

# --- Kapasitas ----------------------------------------------------------------
row("Kapasitas", 26)
bargauge("Disk / per host", [target(
    '100 - node_filesystem_avail_bytes{mountpoint="/",fstype!~"tmpfs|fuse.*"} / node_filesystem_size_bytes{mountpoint="/",fstype!~"tmpfs|fuse.*"} * 100',
    "{{host}}", instant=True)], 0, 27, 8, 7)
bargauge("RAM per host", [target("100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)", "{{host}}", instant=True)],
         8, 27, 8, 7)
bargauge("Storage host pve", [
    target('homelab_lvm_thinpool_used_percent', "thin pool {{lv}} ({{type}})", instant=True, ref="A"),
    target('100 - node_filesystem_avail_bytes{host="pve",mountpoint="/mnt/pve/proxmox-target"} / node_filesystem_size_bytes{host="pve",mountpoint="/mnt/pve/proxmox-target"} * 100',
           "HDD backup (NTFS)", instant=True, ref="B"),
    target('100 - node_filesystem_avail_bytes{host="pve",mountpoint="/mnt/gdrive"} / node_filesystem_size_bytes{host="pve",mountpoint="/mnt/gdrive"} * 100',
           "Google Drive (kuota)", instant=True, ref="C"),
], 16, 27, 8, 7, desc="Thin pool = disk semua LXC. Penuh = LXC berhenti")
stat("Update paket tertunda", [target("sum by (host) (apt_upgrades_pending)", "{{host}}", instant=True)], 0, 34, 24, 3,
     steps=[("green", None), ("orange", 1), ("red", 50)], desc="Dari apt.prom (node exporter). unattended-upgrades memasang patch keamanan otomatis")

# --- Keamanan (Loki) ----------------------------------------------------------
row("Keamanan (log dari Loki)", 37)
timeseries("SSH login gagal", [target('sum by (host) (count_over_time({unit="ssh.service"} |~ "Failed|Invalid user|Connection closed by authenticating" [5m]))', "{{host}}", ds=LOKI)],
           0, 38, 8, 7, ds=LOKI, bars=True)
timeseries("Koneksi diblokir UFW (per tujuan)", [target('sum by (dst) (count_over_time({host="pve"} |= "UFW BLOCK" | regexp "DST=(?P<dst>[0-9.]+)" [5m]))', "{{dst}}", ds=LOKI)],
           8, 38, 8, 7, ds=LOKI, bars=True, desc="Log UFW semua LXC tercatat di kernel pve (nf_log_all_netns)")
timeseries("fail2ban: ban baru", [target('sum by (host) (count_over_time({identifier="fail2ban-server"} |~ "\\\\] Ban " [15m]))', "{{host}}", ds=LOKI)],
           16, 38, 8, 7, ds=LOKI, bars=True)
logs("Login SSH berhasil", '{unit="ssh.service"} |= "Accepted"', 0, 45, 12, 8)
logs("Login Web UI Proxmox gagal", '{host="pve", unit="pvedaemon.service"} |= "authentication failure"', 12, 45, 12, 8,
     desc="Via LAN atau Cloudflare Tunnel (domain publik)")
logs("fail2ban ban / unban", '{identifier="fail2ban-server"} |~ "Ban |Unban "', 0, 53, 12, 8)
logs("Login database (PostgreSQL)", '{unit="postgresql"} |= "connection authorized" != "prometheus@"', 12, 53, 12, 8,
     desc="Tanpa koneksi exporter monitoring")

# --- DR & data tier -----------------------------------------------------------
row("DR & data tier (replikasi DB, Redis, standby)", 61)
stat("Replika DB terhubung", [target("pg_replication_slots_active", "{{slot_name}}", instant=True)], 0, 62, 5, 4,
     steps=[("red", None), ("green", 1)],
     mappings=[{"type": "value", "options": {"0": {"text": "TERPUTUS", "color": "red", "index": 0},
                                             "1": {"text": "STREAMING", "color": "green", "index": 1}}}],
     desc="Replication slot di primary (104) aktif = replika DR (105) menerima WAL")
stat("Lag replika", [target("max(pg_replication_lag_seconds and on(instance) pg_replication_is_replica == 1)", "detik", instant=True)],
     5, 62, 4, 4, unit="s", decimals=0, steps=[("green", None), ("orange", 10), ("red", 60)],
     desc="0 = replika sudah sama dengan primary (RPO ≈ 0)")
stat("WAL tertahan di primary", [target("max(pg_replication_slots_pg_wal_lsn_diff)", "bytes", instant=True)],
     9, 62, 5, 4, unit="bytes", steps=[("green", None), ("orange", 536870912), ("red", 1073741824)],
     desc="Batas 2GB (max_slot_wal_keep_size); lewat itu replika harus resync")
stat("Redis", [target("redis_up", "{{host}}", instant=True)], 14, 62, 4, 4,
     steps=[("red", None), ("green", 1)], mappings=UPDOWN)
bargauge("Memori Redis", [target("100 * redis_memory_used_bytes / redis_memory_max_bytes", "{{host}}", instant=True)],
         18, 62, 6, 4, steps=[("green", None), ("orange", 70), ("red", 80)],
         desc="Policy noeviction: 100% = tulis ditolak")

# --- PITR ---------------------------------------------------------------------
row("PITR - pgBackRest (backup terenkripsi + arsip WAL)", 66)
stat("Backup PITR terakhir", [target("(time() - max(pgbackrest_last_backup_timestamp_seconds)) / 3600", "jam lalu", instant=True)],
     0, 67, 5, 4, unit="h", decimals=1, steps=[("green", None), ("orange", 25), ("red", 26)],
     desc="Full Minggu 01:00, differential Senin-Sabtu 01:00 (diambil dari replika)")
stat("Status repositori", [target("pgbackrest_stanza_status", "{{stanza}}", instant=True)], 5, 67, 4, 4,
     steps=[("green", None), ("red", 1)],
     mappings=[{"type": "value", "options": {"0": {"text": "OK", "color": "green", "index": 0}}}])
stat("WAL terakhir diarsip", [target("time() - max(pg_archiver_last_archived_timestamp_seconds and on(instance) pg_archiver_is_replica == 0)", "detik lalu", instant=True)],
     9, 67, 5, 4, unit="s", decimals=0, steps=[("green", None)],
     desc="Saat ada aktivitas, segmen diarsip maks tiap 60 detik (archive_timeout). DB idle = angka ini membesar tanpa masalah")
stat("Arsip WAL gagal", [target("max(pg_archiver_failed_total and on(instance) pg_archiver_is_replica == 0)", "sejak restart", instant=True)],
     14, 67, 4, 4, steps=[("green", None), ("red", 1)])
stat("Ukuran repositori", [target("max(pgbackrest_repo_size_bytes)", "terkompresi+terenkripsi", instant=True)],
     18, 67, 6, 4, unit="bytes", steps=[("blue", None)])

dashboard = {
    "uid": "homelab-overview", "title": "Homelab Overview", "id": None,
    "description": "Ringkasan homelab Proxmox: host, uptime, alert, backup, kapasitas, keamanan. Dikelola Ansible - perubahan di UI tidak permanen.",
    "tags": ["homelab"], "timezone": "browser", "schemaVersion": 39, "version": 1, "editable": False,
    "refresh": "1m", "time": {"from": "now-24h", "to": "now"}, "graphTooltip": 1,
    "templating": {"list": []}, "annotations": {"list": []},
    "links": [{"title": "Node Exporter Full", "type": "link", "url": "/d/node-exporter-full"},
              {"title": "PostgreSQL", "type": "link", "url": "/d/postgresql"},
              {"title": "Blackbox", "type": "link", "url": "/d/blackbox-http"}],
    "panels": panels,
}
json.dump(dashboard, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
print(f"{len(panels)} panel ditulis ke {sys.argv[1]}")
