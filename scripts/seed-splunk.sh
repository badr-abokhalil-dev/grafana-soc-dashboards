#!/usr/bin/env bash
# Seed Splunk trial with mock SOC data via HEC (HTTP Event Collector)
# Run after: docker compose up -d && sleep 120 (Splunk needs ~2 min to start)
#
# Usage: ./scripts/seed-splunk.sh [HEC_TOKEN]
# If no token passed, creates one automatically.

set -euo pipefail

SPLUNK_URL="${SPLUNK_URL:-https://localhost:8089}"
SPLUNK_HEC="${SPLUNK_HEC:-https://localhost:8088}"
SPLUNK_USER="${SPLUNK_USER:-admin}"
SPLUNK_PASS="${SPLUNK_PASS:-SocDash2026!}"
HEC_TOKEN="${1:-}"

echo "=== SOC Dashboard — Splunk Data Seeder ==="

# --- Wait for Splunk to be ready ---
echo "[1/4] Waiting for Splunk..."
for i in $(seq 1 30); do
  if curl -ks "$SPLUNK_URL/services/server/info" -u "$SPLUNK_USER:$SPLUNK_PASS" | grep -q 'server-info' 2>/dev/null; then
    echo "  Splunk is ready."
    break
  fi
  echo "  Attempt $i/30..."
  sleep 10
done

# --- Create HEC token if not provided ---
if [ -z "$HEC_TOKEN" ]; then
  echo "[2/4] Creating HEC token..."
  HEC_TOKEN=$(curl -ks "$SPLUNK_URL/servicesNS/admin/splunk_httpinput/data/inputs/http" \
    -u "$SPLUNK_USER:$SPLUNK_PASS" \
    -d name=soc-dashboard \
    -d index=main \
    -d sourcetype=soc_events \
    -d output_mode=json | python3 -c "import sys,json; print(json.load(sys.stdin)['entry'][0]['content']['token'])" 2>/dev/null || echo "")

  if [ -z "$HEC_TOKEN" ]; then
    # Token might already exist — fetch it
    HEC_TOKEN=$(curl -ks "$SPLUNK_URL/servicesNS/admin/splunk_httpinput/data/inputs/http/soc-dashboard" \
      -u "$SPLUNK_USER:$SPLUNK_PASS" \
      -d output_mode=json | python3 -c "import sys,json; print(json.load(sys.stdin)['entry'][0]['content']['token'])")
  fi
  echo "  HEC Token: $HEC_TOKEN"
else
  echo "[2/4] Using provided HEC token."
fi

# --- Enable HEC ---
echo "[3/4] Enabling HEC..."
curl -ks "$SPLUNK_URL/servicesNS/admin/splunk_httpinput/data/inputs/http/http/enable" \
  -u "$SPLUNK_USER:$SPLUNK_PASS" \
  -X POST > /dev/null 2>&1 || true

# --- Seed Events ---
echo "[4/4] Seeding events..."

send_event() {
  local event="$1"
  curl -ks "$SPLUNK_HEC/services/collector/event" \
    -H "Authorization: Splunk $HEC_TOKEN" \
    -d "$event" > /dev/null 2>&1
}

# Generate varied security events
SEVERITIES=("critical" "high" "medium" "low")
RULES=("Brute Force Detection" "Suspicious PowerShell" "DNS Tunneling" "Malware Signature" "Phishing URL" "Privilege Escalation" "Lateral Movement" "Tor Exit Node" "Data Exfiltration" "Failed Login Threshold")
ACTIONS=("blocked" "alerted" "quarantined" "alerted" "blocked")
SRC_IPS=("203.0.113.45" "10.0.2.50" "10.0.3.22" "198.51.100.33" "10.0.1.88" "10.0.4.12" "10.0.5.10" "10.0.6.20" "192.168.1.105" "172.16.0.50")
DST_IPS=("10.0.1.15" "10.0.2.50" "198.51.100.10" "10.0.1.5" "192.0.2.100" "10.0.3.15" "10.0.1.44" "198.51.100.77" "10.0.1.95" "10.0.2.77")

NOW=$(date +%s)
COUNT=0

for i in $(seq 1 200); do
  OFFSET=$((RANDOM % 604800))  # random within 7 days
  TS=$((NOW - OFFSET))
  SEV=${SEVERITIES[$((RANDOM % 4))]}
  RULE=${RULES[$((RANDOM % 10))]}
  ACTION=${ACTIONS[$((RANDOM % 5))]}
  SRC=${SRC_IPS[$((RANDOM % 10))]}
  DST=${DST_IPS[$((RANDOM % 10))]}
  HITS=$((RANDOM % 50 + 1))

  send_event "{\"time\": $TS, \"sourcetype\": \"soc_alert\", \"event\": {\"severity\": \"$SEV\", \"rule\": \"$RULE\", \"action\": \"$ACTION\", \"src_ip\": \"$SRC\", \"dst_ip\": \"$DST\", \"count\": $HITS}}"
  COUNT=$((COUNT + 1))
done

# Seed some notable incidents
for i in $(seq 1 30); do
  OFFSET=$((RANDOM % 604800))
  TS=$((NOW - OFFSET))
  SEV=${SEVERITIES[$((RANDOM % 4))]}
  STATUS_OPTS=("open" "in_progress" "resolved" "false_positive")
  STATUS=${STATUS_OPTS[$((RANDOM % 4))]}
  ANALYST="analyst-$((RANDOM % 3 + 1))"
  TTD=$((RANDOM % 20 + 1))
  TTR=$((RANDOM % 180 + 10))

  send_event "{\"time\": $TS, \"sourcetype\": \"soc_incident\", \"event\": {\"severity\": \"$SEV\", \"status\": \"$STATUS\", \"analyst\": \"$ANALYST\", \"ttd_min\": $TTD, \"ttr_min\": $TTR, \"category\": \"${RULES[$((RANDOM % 10))]}\" }}"
  COUNT=$((COUNT + 1))
done

echo ""
echo "✅ Seeded $COUNT events into Splunk"
echo ""
echo "=== Next Steps ==="
echo "1. Open Splunk: http://localhost:8000 (admin / $SPLUNK_PASS)"
echo "2. Open Grafana: http://localhost:3033 (admin / SocDash2026!)"
echo "3. Create a Splunk API token: Settings → Tokens → New Token"
echo "4. Update Grafana datasource with the Splunk token"
echo ""
echo "HEC Token (save this): $HEC_TOKEN"
