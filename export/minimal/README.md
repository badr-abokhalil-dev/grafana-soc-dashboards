# Import Guide

## What's Included
- `datasources.yml` — Infinity datasource configuration
- `soc-mgmt-overview.json` — Management dashboard
- `soc-detail-incidents.json` — Incident drilldown
- `soc-detail-soar.json` — SOAR analytics
- `soc-detail-alerts.json` — Alert analysis

## Steps

### 1. Install Infinity Plugin
```bash
grafana-cli plugins install yesoreyeram-infinity-datasource
systemctl restart grafana-server
```

### 2. Provision Datasources
Copy `datasources.yml` to your Grafana provisioning folder:
```bash
cp datasources.yml /etc/grafana/provisioning/datasources/infinity.yml
systemctl restart grafana-server
```

Or create manually in **Connections → Data Sources → Add**:
- Type: **Infinity**, UID: `mock-data`, Auth: **None**
- Allowed Hosts: your mock server host

### 3. Import Dashboards
**Dashboards → New → Import** — upload each `.json` file.

### Datasource UIDs
Dashboards reference `mock-data`. If your datasource UID differs, find-and-replace `mock-data` in the JSON files before importing.

### Switch to Live Data
Change the datasource from `mock-data` → `splunk-api` or `soar-api` in each panel, then update the URL to your real API endpoint.
