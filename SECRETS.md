# Secrets Management

## Testing (UI Configuration)
During testing, datasource tokens can be configured directly in the Grafana UI.
**Do not use this method in production.**

## Production: Delinea Secret Server

Before going live, integrate with Delinea Secret Server to pull tokens at runtime.

### Secrets to Create in Delinea
- `SOC-Dashboard/Splunk-API-Token`
- `SOC-Dashboard/SOAR-API-Token`
- `SOC-Dashboard/Grafana-Admin-Password`

### Integration Pattern
Container starts → Call Delinea API → Pull secret → Inject into environment → Start

Only the Delinea API credentials need to live on the server. All actual tokens are pulled from Delinea at runtime, never written to disk.

### Steps
1. Give the SOC server's machine account read access to the secrets
2. Use an init container or startup script to fetch secrets before Grafana starts
3. Pass tokens via environment variables to the containers

TODO: Add Delinea fetch script and docker-compose production template.
