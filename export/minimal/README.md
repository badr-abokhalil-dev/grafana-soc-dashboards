# SOC Dashboards — Import Guide

## What's Included
- `yesoreyeram-infinity-datasource/` — Infinity plugin (48MB)
- `datasources.yml` — Datasource configuration
- `infosec-home.json` — **Home dashboard** (entry point with navigation cards)
- `soc-mgmt-overview.json` — Management dashboard
- `soc-detail-incidents.json` — Incident drilldown
- `soc-detail-soar.json` — SOAR analytics
- `soc-detail-alerts.json` — Alert analysis

---

## Step 1: Install Infinity Plugin

Copy the plugin folder to your Grafana plugins directory:
```bash
cp -r yesoreyeram-infinity-datasource /var/lib/grafana/plugins/
chown -R grafana:grafana /var/lib/grafana/plugins/yesoreyeram-infinity-datasource
systemctl restart grafana-server
```

---

## Step 2: Create Datasource

In Grafana UI: **Connections → Data Sources → Add**

| Field | Value |
|-------|-------|
| Type | Infinity |
| UID | `mock-data` |
| Auth | None |
| Allowed Hosts | your mock server host (e.g. `http://localhost:3001`) |
| TLS Skip Verify | `true` |

---

## Step 3: Import Dashboards

**Dashboards → New → Import** — upload each `.json` file:
- `infosec-home.json` (import first — this is your entry point)
- `soc-mgmt-overview.json`
- `soc-detail-incidents.json`
- `soc-detail-soar.json`
- `soc-detail-alerts.json`

---

## Datasource UID

Dashboards reference `mock-data`. If your datasource UID is different, find-and-replace `mock-data` with your UID in all JSON files before importing.

---

## Switch to Live Data

After importing, change each panel's datasource from `mock-data` → `splunk-api` or `soar-api`, then update the URL to your real API endpoint.
