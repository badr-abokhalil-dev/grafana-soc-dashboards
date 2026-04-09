# Import Guide

## What's Included
- `minimal/datasources.yml` — Infinity datasource configuration (Splunk + SOAR + Mock)
- `infosec-home.json` — **Home dashboard** (entry point with navigation cards)
- `soc-mgmt-overview.json` — Management dashboard (incidents, SLA, MITRE, workload, SOAR efficiency)
- `soc-detail-incidents.json` — Incident drilldown
- `soc-detail-soar.json` — SOAR playbook analytics (uses mock SOAR REST API)
- `soc-detail-alerts.json` — Alert analysis

## Architecture

### Datasources
| UID | Name | Purpose | Auth |
|-----|------|---------|------|
| `splunk-api` | Splunk-API | Incidents, alerts, SLA, MITRE, workload | Basic auth (admin/password) |
| `mock-data` | Mock-Data | SOAR playbook data (mock REST API) | None |
| `soar-api` | SOAR-API | Real SOAR (production only) | Bearer token |

### Query Patterns
- **Splunk panels**: POST to `/services/search/jobs/export?output_mode=csv`, search in body, time via `earliest_time`/`latest_time` body params
- **SOAR panels**: GET to `/rest/playbook_run/*` endpoints, time via `start_time`/`end_time` query params
- **Time variables**: `${__from:date:seconds}` / `${__to:date:seconds}` for Splunk; `${__from}` / `${__to}` for mock server

## Steps

### 1. Install Infinity Plugin
```bash
grafana-cli plugins install yesoreyeram-infinity-datasource
systemctl restart grafana-server
```

### 2. Provision Datasources
Copy `minimal/datasources.yml` to your Grafana provisioning folder:
```bash
cp minimal/datasources.yml /etc/grafana/provisioning/datasources/infinity.yml
```
Update the Splunk password and SOAR token environment variables, then restart Grafana.

### 3. Start Mock SOAR Server (for testing)
```bash
cd mock-server && npm install && npm start
# Runs on port 3001 — mimics Splunk SOAR/Phantom REST API
```

### 4. Import Dashboards
**Dashboards → New → Import** — upload each `.json` file.

## Switching to Production

### Splunk
- Splunk API tokens bypass 2FA (RSA SecurID etc.) — create a service token via Settings → Tokens
- Update `SPLUNK_PASSWORD` or switch to bearer token auth in datasources.yml
- Dashboard queries use standard SPL via `/services/search/jobs/export`

### SOAR
- Update `SOAR_API_URL` and `SOAR_API_TOKEN` environment variables
- Change SOAR panel datasource UIDs from `mock-data` → `soar-api`
- Update URLs from `http://soc-mock-server:3001/rest/...` → your SOAR URL
- The mock API endpoints mirror real Splunk SOAR/Phantom REST API structure

### Secrets Management
For production, use Delinea Secret Server (or equivalent) to inject tokens at runtime. See `SECRETS.md`.
