# Mock Server Endpoint Reference

Complete reference for the `soc-mock-server` (Node.js/Express) running at `http://soc-mock-server:3001`.

## General Notes

- **Time filtering**: All endpoints that accept time parameters support ISO 8601 datetime strings, epoch seconds (10 digits), and epoch milliseconds (13 digits)
- **Unsubstituted variables**: If Grafana variables like `${__from}` arrive unsubstituted, the server returns all data (no filtering)
- **CORS**: Enabled for all origins
- **Static data**: All mock data is loaded from `/mock-data/` JSON files at server startup

---

## Incident Endpoints

### GET `/incidents` (alias: `/incidents.json`)

Returns all notable/incident events.

**Query Parameters:**

| Parameter    | Type   | Required | Description                        |
|-------------|--------|----------|------------------------------------|
| `start_time` | string | No       | Filter events with `_time` >= value |
| `end_time`   | string | No       | Filter events with `_time` <= value |

**Response:** JSON array of incident objects.

```json
[
  {
    "event_id": "29439FBC-FFCB-45FF-93C2-420202012E1E@@notable@@75ecb6a3938d",
    "rule_name": "Brute Force Access Behavior Detected",
    "search_name": "Access - Brute Force Access Behavior Detected - Rule",
    "security_domain": "access",
    "severity": "critical",
    "urgency": "critical",
    "status": "1",
    "status_label": "New",
    "owner": "unassigned",
    "src": "203.0.113.45",
    "dest": "10.0.1.15",
    "user": "",
    "source": "Brute Force Access Behavior Detected",
    "_time": "2026-04-05T01:23:00+00:00",
    "info_min_time": "2026-04-05T01:00:00+00:00",
    "info_max_time": "2026-04-05T01:30:00+00:00",
    "tag": "attack,brute_force",
    "mitre_attack_technique": "T1110",
    "mitre_attack_tactic": "credential-access"
  }
]
```

**Field Reference:**

| Field                    | Type   | Values / Description                                |
|--------------------------|--------|-----------------------------------------------------|
| `event_id`               | string | Unique event identifier (UUID format)               |
| `rule_name`              | string | Display name of the correlation rule                |
| `search_name`            | string | Full search name (domain - name - Rule)             |
| `security_domain`        | string | `access`, `endpoint`, `network`, `email`            |
| `severity`               | string | `critical`, `high`, `medium`, `low`                 |
| `urgency`                | string | `critical`, `high`, `medium`, `low`                 |
| `status`                 | string | Numeric: `1`=New, `2`=In Progress, `5`=Closed       |
| `status_label`           | string | `New`, `In Progress`, `Closed`                      |
| `owner`                  | string | Analyst username or `unassigned`                    |
| `src`                    | string | Source IP address or `external`                     |
| `dest`                   | string | Destination IP address                              |
| `user`                   | string | Associated username (may be empty)                  |
| `source`                 | string | Source description                                  |
| `_time`                  | string | ISO 8601 datetime                                   |
| `info_min_time`          | string | ISO 8601 datetime (event window start)              |
| `info_max_time`          | string | ISO 8601 datetime (event window end)                |
| `tag`                    | string | Comma-separated tags                                |
| `mitre_attack_technique` | string | MITRE ATT&CK technique ID (e.g., `T1110`)          |
| `mitre_attack_tactic`    | string | MITRE ATT&CK tactic (e.g., `credential-access`)    |

---

### GET `/incidents/by_category`

Groups incidents by `security_domain`.

**Query Parameters:** None

**Response:**
```json
[
  { "category": "access", "count": 5 },
  { "category": "endpoint", "count": 4 },
  { "category": "network", "count": 3 },
  { "category": "email", "count": 2 }
]
```

---

### GET `/incidents/by_severity`

Groups incidents by severity level.

**Query Parameters:** None

**Response:**
```json
[
  { "severity": "critical", "count": 4 },
  { "severity": "high", "count": 6 },
  { "severity": "medium", "count": 3 },
  { "severity": "low", "count": 1 }
]
```

---

### GET `/incidents/by_owner`

Groups incidents by assigned analyst.

**Query Parameters:** None

**Response:**
```json
[
  { "analyst": "ahmed.ali", "count": 5 },
  { "analyst": "sara.khan", "count": 4 },
  { "analyst": "unassigned", "count": 3 }
]
```

---

### GET `/incidents/by_source`

Groups incidents by MITRE ATT&CK tactic.

**Query Parameters:** None

**Response:**
```json
[
  { "tactic": "credential-access", "count": 4 },
  { "tactic": "execution", "count": 3 },
  { "tactic": "exfiltration", "count": 2 }
]
```

---

### GET `/incidents/by_status`

Groups incidents by status label.

**Query Parameters:** None

**Response:**
```json
[
  { "status": "New", "count": 5 },
  { "status": "In Progress", "count": 4 },
  { "status": "Closed", "count": 5 }
]
```

---

## Alert Endpoints

### GET `/alerts` (alias: `/alerts.json`)

Returns all triggered alerts.

**Query Parameters:**

| Parameter    | Type   | Required | Description                        |
|-------------|--------|----------|------------------------------------|
| `start_time` | string | No       | Filter alerts with `_time` >= value |
| `end_time`   | string | No       | Filter alerts with `_time` <= value |

**Response:** JSON array of alert objects.

```json
[
  {
    "_time": "2026-04-05T05:00:00+00:00",
    "search_name": "Access - Brute Force Access Behavior Detected - Rule",
    "rule_name": "Brute Force Detection",
    "severity": "critical",
    "urgency": "critical",
    "action": "blocked",
    "src": "203.0.113.45",
    "dest": "10.0.1.15",
    "user": "",
    "app": "firewall",
    "vendor_action": "blocked",
    "count": 3
  }
]
```

**Field Reference:**

| Field           | Type   | Values / Description                                |
|-----------------|--------|-----------------------------------------------------|
| `_time`         | string | ISO 8601 datetime                                   |
| `search_name`   | string | Full correlation search name                        |
| `rule_name`     | string | Short display name                                  |
| `severity`      | string | `critical`, `high`, `medium`, `low`                 |
| `urgency`       | string | `critical`, `high`, `medium`, `low`                 |
| `action`        | string | `blocked`, `allowed`                                |
| `src`           | string | Source IP address                                   |
| `dest`          | string | Destination IP address                              |
| `user`          | string | Associated username (may be empty)                  |
| `app`           | string | `firewall`, `sysmon`, `dns`, `antivirus`, `proxy`, `vpn`, `email_gateway` |
| `vendor_action` | string | `blocked`, `alerted`, `quarantined`                 |
| `count`         | number | Number of matching events                           |

---

## SLA Metrics Endpoint

### GET `/sla-metrics` (alias: `/sla-metrics.json`)

Returns weekly SLA compliance metrics.

**Query Parameters:**

| Parameter    | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| `start_time` | string | No       | Filter weeks overlapping with this start time     |
| `end_time`   | string | No       | Filter weeks overlapping with this end time       |

> Time filtering uses ISO week boundaries. A week is included if it overlaps with the requested time range.

**Response:** JSON array of weekly SLA metric objects.

```json
[
  {
    "period": "2026-W13",
    "total_incidents": 35,
    "sla_met": 31,
    "sla_breached": 4,
    "avg_mttd_min": 6.2,
    "avg_mttr_min": 62,
    "false_positive_rate": 0.12,
    "escalation_rate": 0.08,
    "sla_compliance": 0.89
  }
]
```

**Field Reference:**

| Field                | Type   | Description                                    |
|----------------------|--------|------------------------------------------------|
| `period`             | string | ISO week format (e.g., `2026-W13`)             |
| `total_incidents`    | number | Total incidents in the week                    |
| `sla_met`            | number | Incidents resolved within SLA                  |
| `sla_breached`       | number | Incidents that breached SLA                    |
| `avg_mttd_min`       | number | Average mean time to detect (minutes)          |
| `avg_mttr_min`       | number | Average mean time to respond (minutes)         |
| `false_positive_rate` | number | Decimal 0.0-1.0                               |
| `escalation_rate`    | number | Decimal 0.0-1.0                               |
| `sla_compliance`     | number | Decimal 0.0-1.0                               |

---

## Playbook Catalog Endpoint

### GET `/playbooks.json`

Returns the catalog of all configured playbooks with run statistics.

**Query Parameters:**

| Parameter    | Type   | Required | Description                                 |
|-------------|--------|----------|---------------------------------------------|
| `start_time` | string | No       | Filter by `last_run_time` >= value           |
| `end_time`   | string | No       | Filter by `last_run_time` <= value           |

**Response:** JSON array of playbook objects.

```json
[
  {
    "id": 1,
    "name": "Phishing Response",
    "playbook_run_count": 48,
    "successful_run_count": 44,
    "failed_run_count": 4,
    "avg_duration_seconds": 180,
    "last_run_time": "2026-04-04T14:35:00Z",
    "active": true,
    "category": "Email Security",
    "creator": "ahmed.ali",
    "tags": ["phishing", "email", "automated"],
    "success_rate": 0.917
  }
]
```

**Field Reference:**

| Field                  | Type     | Description                          |
|------------------------|----------|--------------------------------------|
| `id`                   | number   | Playbook ID                          |
| `name`                 | string   | Playbook display name                |
| `playbook_run_count`   | number   | Total runs                           |
| `successful_run_count` | number   | Successful runs                      |
| `failed_run_count`     | number   | Failed runs                          |
| `avg_duration_seconds` | number   | Average run duration in seconds      |
| `last_run_time`        | string   | ISO 8601 datetime of last run        |
| `active`               | boolean  | Whether playbook is enabled          |
| `category`             | string   | Category name                        |
| `creator`              | string   | Username who created the playbook    |
| `tags`                 | string[] | Array of tag strings                 |
| `success_rate`         | number   | Decimal 0.0-1.0                      |

---

## Analyst Workload Endpoint

### GET `/analyst-workload.json`

Returns current workload metrics per analyst. No time filtering.

**Query Parameters:** None

**Response:** JSON array of analyst workload objects.

```json
[
  {
    "analyst": "ahmed.ali",
    "open_incidents": 2,
    "resolved_today": 1,
    "resolved_week": 12,
    "avg_ttr_min": 58,
    "sla_compliance": 0.92
  }
]
```

**Field Reference:**

| Field            | Type   | Description                              |
|------------------|--------|------------------------------------------|
| `analyst`        | string | Analyst username                         |
| `open_incidents` | number | Currently open/assigned incidents        |
| `resolved_today` | number | Incidents resolved today                 |
| `resolved_week`  | number | Incidents resolved this week             |
| `avg_ttr_min`    | number | Average time to resolve (minutes)        |
| `sla_compliance` | number | Decimal 0.0-1.0                          |

---

## MITRE Coverage Endpoint

### GET `/mitre-coverage.json`

Returns MITRE ATT&CK coverage statistics per tactic. No time filtering.

**Query Parameters:** None

**Response:** JSON array of tactic coverage objects.

```json
[
  {
    "tactic": "Initial Access",
    "techniques_covered": 8,
    "techniques_total": 9,
    "detections_30d": 48,
    "top_technique": "T1566 Phishing"
  }
]
```

**Field Reference:**

| Field               | Type   | Description                                  |
|---------------------|--------|----------------------------------------------|
| `tactic`            | string | MITRE ATT&CK tactic name                    |
| `techniques_covered` | number | Number of techniques with active detections |
| `techniques_total`  | number | Total techniques in the tactic               |
| `detections_30d`    | number | Detection count in last 30 days              |
| `top_technique`     | string | Most-detected technique (ID + name)          |

---

## SOAR Playbook Run Endpoints

### GET `/rest/playbook_run` (alias: `/playbook_runs.json`)

Returns individual playbook run records.

**Query Parameters:**

| Parameter    | Type   | Required | Default          | Description                          |
|-------------|--------|----------|------------------|--------------------------------------|
| `start_time` | string | No       | —                | Filter by `start_time` >= value      |
| `end_time`   | string | No       | —                | Filter by `start_time` <= value      |
| `limit`      | number | No       | 1000             | Maximum results to return            |
| `order`      | string | No       | `-start_time`    | Sort: `-start_time` (desc) or `start_time` (asc) |

**Response:** Wrapped object with count and results array.

```json
{
  "count": 50,
  "results": [
    {
      "id": 2707,
      "playbook": 8,
      "container": 2557,
      "owner": 12,
      "status": "success",
      "start_time": "2026-04-04T17:17:14.000Z",
      "update_time": "2026-04-04T17:17:23.000Z",
      "message": "{\"status\": \"success\"}",
      "cancelled": "",
      "test_mode": false,
      "log_level": 1
    }
  ]
}
```

**Field Reference:**

| Field         | Type        | Description                               |
|---------------|-------------|-------------------------------------------|
| `id`          | number      | Playbook run ID                           |
| `playbook`    | number      | Playbook ID                               |
| `container`   | number      | Container (event/case) ID                 |
| `owner`       | number/null | Owner user ID                             |
| `status`      | string      | `success` or `failed`                     |
| `start_time`  | string      | ISO 8601 datetime                         |
| `update_time` | string      | ISO 8601 datetime                         |
| `message`     | string      | JSON string with status details           |
| `cancelled`   | string      | Cancellation reason (empty if not cancelled) |
| `test_mode`   | boolean     | Whether run was in test mode              |
| `log_level`   | number      | Logging level                             |

---

### GET `/rest/playbook_run/stats`

Returns aggregated playbook run statistics.

**Query Parameters:**

| Parameter    | Type   | Required | Description                                       |
|-------------|--------|----------|---------------------------------------------------|
| `start_time` | string | No       | Filter by time range                               |
| `end_time`   | string | No       | Filter by time range                               |
| `format`     | string | No       | `columns` for Grafana table format, omit for flat  |

**Response (default - flat array):**

```json
[
  {
    "total_runs": 50,
    "successful_runs": 42,
    "failed_runs": 8,
    "success_rate": 0.84,
    "avg_duration_seconds": 125.5
  }
]
```

**Response (format=columns):**

```json
{
  "columns": [
    { "text": "total_runs", "type": "number" },
    { "text": "successful_runs", "type": "number" },
    { "text": "failed_runs", "type": "number" },
    { "text": "success_rate", "type": "number" },
    { "text": "avg_duration_seconds", "type": "number" }
  ],
  "rows": [[50, 42, 8, 0.84, 125.5]]
}
```

---

### GET `/rest/playbook_run/per_playbook`

Returns per-playbook aggregated run statistics.

**Query Parameters:**

| Parameter    | Type   | Required | Description          |
|-------------|--------|----------|----------------------|
| `start_time` | string | No       | Filter by time range |
| `end_time`   | string | No       | Filter by time range |

**Response:**

```json
[
  {
    "id": 1,
    "name": "Phishing Response",
    "category": "Email Security",
    "active": true,
    "playbook_run_count": 48,
    "successful_run_count": 44,
    "failed_run_count": 4,
    "avg_duration_seconds": 180.0,
    "success_rate": 0.917
  }
]
```

---

### GET `/rest/playbook_run/by_category`

Returns playbook run counts grouped by category.

**Query Parameters:**

| Parameter    | Type   | Required | Description          |
|-------------|--------|----------|----------------------|
| `start_time` | string | No       | Filter by time range |
| `end_time`   | string | No       | Filter by time range |

**Response:**

```json
[
  { "category": "Email Security", "playbook_run_count": 48 },
  { "category": "Endpoint", "playbook_run_count": 22 },
  { "category": "Network", "playbook_run_count": 15 }
]
```

---

## SOAR Action Run Endpoints

### GET `/rest/action_run` (alias: `/action_runs.json`)

Returns individual action run records.

**Query Parameters:**

| Parameter    | Type   | Required | Default          | Description                              |
|-------------|--------|----------|------------------|------------------------------------------|
| `start_time` | string | No       | —                | Filter by `create_time` >= value         |
| `end_time`   | string | No       | —                | Filter by `create_time` <= value         |
| `limit`      | number | No       | 1000             | Maximum results to return                |
| `order`      | string | No       | `-create_time`   | Sort: `-create_time` (desc) or `create_time` (asc) |

**Response:** Wrapped object with count and results array.

```json
{
  "count": 100,
  "results": [
    {
      "id": 2607,
      "action": "create ticket",
      "container": 2557,
      "create_time": "2026-04-04T17:17:14.000Z",
      "close_time": "2026-04-04T17:17:23.000Z",
      "message": "1 actions succeeded",
      "name": "automated action 'create ticket' of 'ticket_escalation' playbook",
      "owner": 12,
      "playbook": 8,
      "playbook_run": 2707,
      "status": "success",
      "type": "correct",
      "update_time": "2026-04-04T17:17:23.000Z"
    }
  ]
}
```

**Field Reference:**

| Field          | Type        | Description                                          |
|----------------|-------------|------------------------------------------------------|
| `id`           | number      | Action run ID                                        |
| `action`       | string      | Action name (e.g., `create ticket`, `block domain`)  |
| `container`    | number      | Container (event/case) ID                            |
| `create_time`  | string      | ISO 8601 datetime                                    |
| `close_time`   | string      | ISO 8601 datetime                                    |
| `message`      | string      | Result message                                       |
| `name`         | string      | Full action description                              |
| `owner`        | number/null | Owner user ID                                        |
| `playbook`     | number      | Playbook ID                                          |
| `playbook_run` | number      | Parent playbook run ID                               |
| `status`       | string      | `success` or `failed`                                |
| `type`         | string      | `correct`, `investigate`, or `contain`               |
| `update_time`  | string      | ISO 8601 datetime                                    |

---

### GET `/action_runs_recent.json`

Same as `/rest/action_run` but sorted descending with default limit of 100.

**Query Parameters:** Same as `/rest/action_run`.

---

### GET `/rest/action_run/stats` (alias: `/soar_daily_stats.json`)

Returns daily aggregated action run statistics.

**Query Parameters:**

| Parameter    | Type   | Required | Default | Description                        |
|-------------|--------|----------|---------|------------------------------------|
| `start_time` | string | No       | —       | Filter by time range               |
| `end_time`   | string | No       | —       | Filter by time range               |
| `group_by`   | string | No       | `day`   | Aggregation period                 |

**Response:** Wrapped object with count and results array.

```json
{
  "count": 30,
  "results": [
    {
      "date": "2025-10-07T00:00:00.000Z",
      "total": 11,
      "success": 10,
      "failed": 1,
      "success_rate": 0.909
    }
  ]
}
```

**Field Reference:**

| Field          | Type   | Description              |
|----------------|--------|--------------------------|
| `date`         | string | ISO 8601 date            |
| `total`        | number | Total actions on date    |
| `success`      | number | Successful actions       |
| `failed`       | number | Failed actions           |
| `success_rate` | number | Decimal 0.0-1.0          |

---

### GET `/rest/action_run/summary` (alias: `/soar_action_summary.json`)

Returns summary statistics grouped by action type. No time filtering.

**Query Parameters:** None

**Response:** Wrapped object with count and results array (REST endpoint) or flat array (alias).

```json
[
  {
    "action": "get process list",
    "total": 284,
    "success": 264,
    "failed": 20,
    "success_rate": 0.93
  },
  {
    "action": "block domain",
    "total": 274,
    "success": 254,
    "failed": 20,
    "success_rate": 0.927
  }
]
```

**Field Reference:**

| Field          | Type   | Description                     |
|----------------|--------|---------------------------------|
| `action`       | string | Action type name                |
| `total`        | number | Total executions                |
| `success`      | number | Successful executions           |
| `failed`       | number | Failed executions               |
| `success_rate` | number | Decimal 0.0-1.0                 |

---

## Debug Endpoint

### GET `/debug/params`

Echoes back all received query parameters. Useful for debugging Grafana variable substitution.

**Response:**
```json
{
  "query": {
    "start_time": "${__from}",
    "end_time": "${__to}"
  }
}
```

---

## Endpoint Summary Table

| Endpoint                         | Method | Time Filter | Response Type     | Alias                      |
|----------------------------------|--------|-------------|-------------------|----------------------------|
| `/incidents`                     | GET    | Yes         | Array             | `/incidents.json`          |
| `/incidents/by_category`         | GET    | No          | Array             | —                          |
| `/incidents/by_severity`         | GET    | No          | Array             | —                          |
| `/incidents/by_owner`            | GET    | No          | Array             | —                          |
| `/incidents/by_source`           | GET    | No          | Array             | —                          |
| `/incidents/by_status`           | GET    | No          | Array             | —                          |
| `/alerts`                        | GET    | Yes         | Array             | `/alerts.json`             |
| `/sla-metrics`                   | GET    | Yes         | Array             | `/sla-metrics.json`        |
| `/playbooks.json`                | GET    | Yes         | Array             | —                          |
| `/analyst-workload.json`         | GET    | No          | Array             | —                          |
| `/mitre-coverage.json`           | GET    | No          | Array             | —                          |
| `/rest/playbook_run`             | GET    | Yes         | `{count, results}` | `/playbook_runs.json`     |
| `/rest/playbook_run/stats`       | GET    | Yes         | Array or `{columns, rows}` | —              |
| `/rest/playbook_run/per_playbook`| GET    | Yes         | Array             | —                          |
| `/rest/playbook_run/by_category` | GET    | Yes         | Array             | —                          |
| `/rest/action_run`               | GET    | Yes         | `{count, results}` | `/action_runs.json`       |
| `/action_runs_recent.json`       | GET    | Yes         | `{count, results}` | —                         |
| `/rest/action_run/stats`         | GET    | Yes         | `{count, results}` | `/soar_daily_stats.json`  |
| `/rest/action_run/summary`       | GET    | No          | `{count, results}` | `/soar_action_summary.json` |
| `/debug/params`                  | GET    | No          | Object            | —                          |
