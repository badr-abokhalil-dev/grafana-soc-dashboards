# Migrating from Mock Data to Live Splunk

## Current Architecture

- **Data Source**: Mock data served by `soc-mock-server` (Node.js) at http://soc-mock-server:3001
- **Dashboards**: 4 Grafana dashboards with Infinity plugin querying mock endpoints
- **Time Filtering**: Mock server supports `start_time`/`end_time` query params

## Mock Endpoints (current)

```
http://soc-mock-server:3001/incidents.json
http://soc-mock-server:3001/alerts.json
http://soc-mock-server:3001/sla-metrics.json
http://soc-mock-server:3001/playbooks.json
http://soc-mock-server:3001/analyst-workload.json
http://soc-mock-server:3001/mitre-coverage.json
http://soc-mock-server:3001/playbook_runs.json
http://soc-mock-server:3001/action_runs.json
http://soc-mock-server:3001/soar_daily_stats.json
http://soc-mock-server:3001/soar_action_summary.json
```

## Splunk Endpoints (target)

```
http://soc-splunk:8089/services/search/jobs/export
http://soc-splunk:8089/services/server/info
```

Splunk REST API uses SPL queries sent via GET/POST to `/services/search/jobs/export` with parameters:

| Parameter     | Description                                        |
|---------------|----------------------------------------------------|
| `search`      | SPL query string (must be URL-encoded)             |
| `earliest`    | Start time (epoch or relative like `-7d`)          |
| `latest`      | End time (epoch or relative like `now`)            |
| `output_mode` | `json` for JSON output (default is XML)            |

## Migration Steps

### 1. Update Infinity Datasource URL

- Change the Mock-Data datasource URL from `http://soc-mock-server:3001` to `http://soc-splunk:8089`
- Update `allowedHosts` in the Infinity datasource provisioning to include `soc-splunk` and `soc-splunk:8089`
- Set authentication to Bearer Token using the `SPLUNK_API_TOKEN` environment variable

### 2. Switch Panel Queries

Each panel's Infinity query needs to be rewritten from mock JSON paths to Splunk SPL queries.

**Example transformation:**

Mock query:
```
GET http://soc-mock-server:3001/incidents.json?start_time=${__from}&end_time=${__to}
```

Splunk query:
```
POST http://soc-splunk:8089/services/search/jobs/export
  search=search index=notable | head 100
  earliest=${__from:date:epoch}
  latest=${__to:date:epoch}
  output_mode=json
```

> **Note:** SPL queries must be URL-encoded when passed as query parameters in GET requests.

### 3. Dashboard Changes Per File

| Dashboard File           | Panels to Rewrite | Key Mock Endpoints Used                                   |
|--------------------------|--------------------|-----------------------------------------------------------|
| `soc-mgmt-overview.json`    | 12 panel queries   | incidents, alerts, sla-metrics, analyst-workload, mitre-coverage |
| `soc-detail-incidents.json` | 8 panel queries    | incidents, incidents/by_severity, incidents/by_status      |
| `soc-detail-alerts.json`    | 8 panel queries    | alerts                                                     |
| `soc-detail-soar.json`      | 8 panel queries    | playbook_runs, action_runs, soar_daily_stats, soar_action_summary |

### 4. Key Differences

| Aspect          | Mock Server                          | Splunk                                                        |
|-----------------|--------------------------------------|---------------------------------------------------------------|
| Response format | JSON array of objects                | JSON with nested structure (`results` array inside response)  |
| Field names     | Consistent mock field names          | Vary by index and sourcetype                                  |
| Authentication  | None                                 | Bearer token or basic auth required                           |
| Time params     | `start_time` / `end_time` (ISO/epoch) | `earliest` / `latest` (epoch or relative)                    |
| Root selector   | Not needed (top-level array)         | Required in Infinity config to extract `results` array        |
| URL encoding    | Not needed                           | SPL queries must be URL-encoded                               |

## Field Name Mapping (Mock to Splunk)

### Incidents / Notable Events

| Mock Field             | Splunk Field (typical)          | Notes                              |
|------------------------|---------------------------------|------------------------------------|
| `event_id`             | `event_id`                      | Same in ES notable events          |
| `rule_name`            | `rule_name`                     | Same in ES notable events          |
| `search_name`          | `search_name`                   | Same in ES notable events          |
| `security_domain`      | `security_domain`               | Same in ES notable events          |
| `severity`             | `severity`                      | Same in ES notable events          |
| `urgency`              | `urgency`                       | Same in ES notable events          |
| `status`               | `status`                        | Numeric (1=New, 2=In Progress, etc.) |
| `status_label`         | `status_label`                  | Derived from status                |
| `owner`                | `owner`                         | Same in ES notable events          |
| `src`                  | `src`                           | Same in ES notable events          |
| `dest`                 | `dest`                          | Same in ES notable events          |
| `user`                 | `user`                          | Same in ES notable events          |
| `_time`                | `_time`                         | Universal Splunk field             |
| `mitre_attack_technique` | `mitre_attack_technique`      | Requires ES Content Update         |
| `mitre_attack_tactic`  | `mitre_attack_tactic`           | Requires ES Content Update         |

### Alerts

| Mock Field       | Splunk Field        | Notes                                    |
|------------------|---------------------|------------------------------------------|
| `search_name`    | `search_name`       | Same                                     |
| `severity`       | `severity`          | Same                                     |
| `action`         | `action`            | Same                                     |
| `vendor_action`  | `vendor_action`     | Same in CIM-compliant data               |
| `count`          | `count`             | May need SPL `stats count` instead       |

### SOAR / Phantom Fields

| Mock Field       | Splunk SOAR Field   | Notes                                    |
|------------------|---------------------|------------------------------------------|
| `playbook`       | `playbook`          | Playbook ID                              |
| `container`      | `container`         | Container (event) ID                     |
| `status`         | `status`            | success / failed                         |
| `start_time`     | `start_time`        | ISO 8601                                 |
| `create_time`    | `create_time`       | ISO 8601                                 |

> **Note:** Splunk field names for ES notable events are largely identical to the mock data since the mock data was modeled after Splunk ES. SOAR fields come from the Splunk SOAR REST API, not Splunk search.

## Auth Setup

The Splunk API datasource uses Bearer Token authentication.

### Configuration Options

**Option A: Environment Variable (recommended for Docker/Kubernetes)**
```yaml
# In docker-compose.yml or Grafana provisioning
environment:
  - SPLUNK_API_TOKEN=your-token-here
```

**Option B: Grafana Provisioning (secureJsonData)**
```yaml
# In datasource provisioning YAML
datasources:
  - name: Splunk-API
    type: yesoreyeram-infinity-datasource
    access: proxy
    url: http://soc-splunk:8089
    jsonData:
      allowedHosts:
        - soc-splunk
        - soc-splunk:8089
    secureJsonData:
      bearerToken: ${SPLUNK_API_TOKEN}
```

**Option C: Grafana UI**
1. Go to Configuration > Data Sources
2. Select or create the Infinity datasource
3. Set URL to `http://soc-splunk:8089`
4. Under Authentication, select Bearer Token
5. Enter the Splunk API token

## SPL Query Examples

### Incidents (replaces `/incidents.json`)
```spl
search index=notable
| fields event_id, rule_name, search_name, security_domain, severity, urgency, status, owner, src, dest, user, _time, mitre_attack_technique, mitre_attack_tactic
| sort -_time
| head 100
```

### Alerts (replaces `/alerts.json`)
```spl
search index=_audit action=alert_fired
| fields _time, search_name, severity, urgency, action, src, dest, user, app, vendor_action
| sort -_time
| head 100
```

### Incidents by Severity (replaces `/incidents/by_severity`)
```spl
search index=notable
| stats count by severity
```

### Incidents by Status (replaces `/incidents/by_status`)
```spl
search index=notable
| stats count by status_label
```

## Grafana Variable Mapping

| Grafana Variable   | Mock Usage                     | Splunk Usage                      |
|--------------------|--------------------------------|-----------------------------------|
| `${__from}`        | `start_time=${__from}`         | `earliest=${__from:date:epoch}`   |
| `${__to}`          | `end_time=${__to}`             | `latest=${__to:date:epoch}`       |
| `${__from_ms}`     | Epoch ms start time            | Convert: `earliest=${__from:date:epoch}` |
| `${__to_ms}`       | Epoch ms end time              | Convert: `latest=${__to:date:epoch}` |

## Infinity Plugin Configuration

When switching to Splunk, update the Infinity panel query settings:

| Setting          | Mock Value                      | Splunk Value                                      |
|------------------|---------------------------------|---------------------------------------------------|
| Type             | JSON                            | JSON                                              |
| Source           | URL                             | URL                                               |
| Method           | GET                             | GET or POST                                       |
| URL              | `http://soc-mock-server:3001/...` | `http://soc-splunk:8089/services/search/jobs/export` |
| Root Selector    | (empty or `$`)                  | `$.results` or `$.results[*]`                     |
| URL params       | `start_time`, `end_time`        | `search`, `earliest`, `latest`, `output_mode`     |

## Important Notes

- Splunk SPL queries must be URL-encoded when passed as query params
- Use `output_mode=json` for JSON response (default is XML)
- Grafana `${__from_ms}` and `${__to_ms}` variables provide epoch milliseconds; Splunk expects epoch seconds, so use `${__from:date:epoch}` and `${__to:date:epoch}` instead
- Infinity plugin `root_selector` must match Splunk JSON response structure (typically `$.results`)
- Mock server can remain running for testing; dashboards can use either datasource by switching the datasource reference
- Consider creating a separate Infinity datasource for Splunk rather than modifying the existing mock datasource, allowing side-by-side comparison during migration
