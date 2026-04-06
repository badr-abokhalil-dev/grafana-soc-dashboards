# 🛡️ SOC Dashboard Skeleton

A portable, self-contained SOC (Security Operations Center) dashboard built with **Grafana OSS** + **Splunk Trial** + **Infinity Plugin**. No Enterprise licensing needed. No middleware.

## Architecture

```
Grafana OSS ──(Infinity Plugin)──► Splunk REST API (oneshot searches)
                                 ├► /services/search/jobs/export (SPL queries)
                                 └► SOAR REST API (when ready)
```

## Quick Start

```bash
# 1. Clone / copy this folder
cd soc-dashboard

# 2. Copy and edit env
cp .env.example .env

# 3. Start everything
docker compose up -d

# 4. Wait ~2 minutes for Splunk to initialize, then seed data
chmod +x scripts/seed-splunk.sh
./scripts/seed-splunk.sh

# 5. Open dashboards
# Grafana: http://localhost:3033 (admin / SocDash2026!)
# Splunk:  http://localhost:8000 (admin / SocDash2026!)
```

## Dashboard Structure

### 📊 SOC Management (Executive View)
| Panel | Description |
|-------|-------------|
| Open Incidents | Count of active incidents |
| Critical Open | Critical severity, unresolved |
| Avg MTTD | Mean Time to Detect (minutes) |
| Avg MTTR | Mean Time to Respond (minutes) |
| SLA Compliance | % of incidents within SLA |
| False Positive Rate | Noise ratio gauge |
| Severity Breakdown | Donut chart by severity |
| SLA Trends | Weekly MTTD/MTTR timeseries |
| SOAR Efficiency | Playbook success rate bars |
| Analyst Workload | Table with SLA per analyst |
| MITRE Coverage | Coverage % per ATT&CK tactic |
| Active Incidents | Full incident table |

### 🔍 SOC Detailed Views
- **Incident Drilldown** — Category breakdown, MITRE heatmap, TTD/TTR histograms, filterable by severity/status/analyst
- **SOAR Playbook Drilldown** — Success/failure per playbook, execution times, category split
- **Alert Analysis** — Rule effectiveness, action breakdown, source IPs, severity distribution, full alert log

## Data Modes

### Mock Mode (default)
Dashboards read from static JSON files in `mock-data/`. No Splunk or SOAR connection needed.

### Live Mode
1. Create a Splunk API token: Splunk → Settings → Tokens → New Token
2. Update the Grafana Splunk-API datasource with the token
3. Edit panel queries to use `POST https://splunk:8089/services/search/jobs/export` with SPL

### SOAR Integration
Same pattern — configure the SOAR-API datasource with your SOAR URL and token. Infinity calls the REST API directly.

## Splunk Oneshot Query Pattern

For Grafana Infinity to query Splunk without middleware:

```
Method: POST
URL: https://splunk:8089/services/search/jobs/export
Headers: Authorization: Bearer <token>
Body (form):
  search = search index=notable | stats count by severity
  output_mode = json
  exec_mode = oneshot
```

This returns results synchronously — no job polling needed.

## Expanding the Dashboard

### Adding New Panels
1. Add mock data to `mock-data/` (new JSON file)
2. Create panel in Grafana UI pointing to Mock-Data datasource
3. Save dashboard JSON → commit

### Adding New Dashboard Views
1. Create JSON in `grafana/dashboards/management/` or `grafana/dashboards/detailed/`
2. Tag with `soc` + `management` or `soc` + `detailed`
3. Navigation links auto-discover by tag

### Adding New Data Sources
1. Add Infinity datasource in `grafana/provisioning/datasources/datasources.yml`
2. Reference with `{"uid": "your-ds-uid"}` in panels

## Folder Structure

```
soc-dashboard/
├── docker-compose.yml
├── .env.example
├── README.md
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/datasources.yml
│   │   └── dashboards/dashboards.yml
│   └── dashboards/
│       ├── management/
│       │   └── soc-overview.json        # Executive KPIs
│       └── detailed/
│           ├── incident-drilldown.json   # Incident deep-dive
│           ├── soar-drilldown.json       # SOAR analytics
│           └── alert-analysis.json       # Alert trends
├── mock-data/
│   ├── incidents.json
│   ├── alerts.json
│   ├── playbooks.json
│   ├── sla-metrics.json
│   ├── analyst-workload.json
│   └── mitre-coverage.json
└── scripts/
    └── seed-splunk.sh
```

## Porting to Work Environment

1. Export dashboards as JSON (or copy this entire folder)
2. Install Infinity plugin on work Grafana: `grafana-cli plugins install yesoreyeram-infinity-datasource`
3. Configure datasources pointing to your real Splunk/SOAR
4. Import dashboard JSONs
5. Update panel queries with real SPL / SOAR API paths
6. Adjust thresholds to match your SLA targets

## Requirements

- Docker + Docker Compose
- ~4GB RAM (Splunk is hungry)
- Ports: 3033 (Grafana), 8000/8088/8089 (Splunk)
