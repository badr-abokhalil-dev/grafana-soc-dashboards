# SOC Dashboard — Import Guide (Offline / Work Environment)

## Prerequisites
- Grafana OSS already installed
- Infinity plugin already installed (see below if not)

---

## Step 1: Install Infinity Plugin (Offline)

If Grafana has internet access:
```bash
grafana-cli plugins install yesoreyeram-infinity-datasource
```

If **offline**, transfer the plugin from a machine that has it:
```bash
# On a machine WITH internet, download the plugin folder:
grafana-cli plugins install yesoreyeram-infinity-datasource
cp -r /var/lib/grafana/plugins/yesoreyeram-infinity-datasource /path/to/copy/

# On the offline machine, place it in:
/var/lib/grafana/plugins/yesoreyeram-infinity-datasource
chown -R grafana:grafana /var/lib/grafana/plugins/yesoreyeram-infinity-datasource
```

Restart Grafana after installing.

---

## Step 2: Create Datasources

In Grafana UI: **Connections → Data Sources → Add**

### Mock-Data (for testing with mock server)
- Type: **Infinity**
- UID: `mock-data`
- Auth: **None**
- Allowed Hosts: `http://your-mock-server:3001`
- TLS Skip Verify: `true`

### Splunk-API (when connecting to real Splunk)
- Type: **Infinity**
- UID: `splunk-api`
- Auth: **Bearer Token** → your Splunk API token
- Allowed Hosts: `https://your-splunk-host:8089`
- TLS Skip Verify: `true` (if using self-signed cert)

### SOAR-API (when connecting to real SOAR)
- Type: **Infinity**
- UID: `soar-api`
- Auth: **Bearer Token** → your SOAR API token
- Allowed Hosts: `https://your-soar-host`
- TLS Skip Verify: `true`

> **UIDs must match exactly** — dashboards reference `mock-data`, `splunk-api`, `soar-api`. If yours differ, do a find-and-replace in the JSON files before importing.

---

## Step 3: Import Dashboards

**Option A — Import via JSON files:**
1. Grafana UI → **Dashboards → New → Import**
2. Upload each JSON file from `export/`:
   - `soc-mgmt-overview.json` → SOC Management
   - `soc-detail-incidents.json` → SOC Detailed
   - `soc-detail-alerts.json` → SOC Detailed
   - `soc-detail-soar.json` → SOC Detailed

**Option B — Provision automatically:**
Copy the provisioning folder to your Grafana:
```bash
cp -r grafana/provisioning/ /etc/grafana/provisioning/
cp -r grafana/dashboards/ /var/lib/grafana/dashboards/
systemctl restart grafana-server
```

---

## Step 4: Configure Datasources in Provisioning (Optional)

If using file-based provisioning, add to `/etc/grafana/provisioning/datasources/datasources.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Mock-Data
    type: yesoreyeram-infinity-datasource
    uid: mock-data
    access: proxy
    isDefault: true
    jsonData:
      auth_method: "none"
      tlsSkipVerify: true
      allowedHosts:
        - "http://your-mock-server:3001"
    editable: true

  - name: Splunk-API
    type: yesoreyeram-infinity-datasource
    uid: splunk-api
    access: proxy
    jsonData:
      auth_method: "bearerToken"
      tlsSkipVerify: true
      allowedHosts:
        - "https://your-splunk-host:8089"
    secureJsonData:
      bearerToken: "YOUR_TOKEN"
    editable: true

  - name: SOAR-API
    type: yesoreyeram-infinity-datasource
    uid: soar-api
    access: proxy
    jsonData:
      auth_method: "bearerToken"
      tlsSkipVerify: true
      allowedHosts:
        - "https://your-soar-host"
    secureJsonData:
      bearerToken: "YOUR_TOKEN"
    editable: true
```

---

## Switching Panels from Mock → Live

Each panel queries a mock URL like `http://soc-mock-server:3001/playbooks.json`. To switch to real data:

1. Change the **datasource** from `mock-data` → `splunk-api` or `soar-api`
2. Change the **URL** to your real API endpoint

Example — SOAR panel:
```
Mock:  GET http://soc-mock-server:3001/rest/playbook_run
Live:  GET https://your-soar-host/rest/playbook_run
       Headers: Authorization: Bearer YOUR_TOKEN
```

---

## Offline Mock Server

If you want to run the mock server offline too, it's a Node.js app. Transfer the folder and run:
```bash
cd mock-server && npm install
node server.js
```

No external dependencies — just Express and CORS (both in `package.json`).
