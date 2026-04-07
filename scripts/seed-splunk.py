#!/usr/bin/env python3
"""Push all mock data to Splunk via HEC (HTTP Event Collector)."""

import json
import urllib.request
import ssl
import os
import sys
from datetime import datetime

SPLUNK_HEC_URL = "https://localhost:8188/services/collector"
HEC_TOKEN = "2f9bb250-8a36-4137-90f9-29ab9f495565"
MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock-data")

# Disable SSL verification for self-signed cert
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def iso_to_epoch(ts):
    """Convert ISO timestamp to epoch seconds."""
    if not ts:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.timestamp()
        except ValueError:
            continue
    return None


def send_events(events_batch):
    """Send a batch of HEC events (newline-delimited JSON)."""
    payload = "\n".join(json.dumps(e) for e in events_batch)
    req = urllib.request.Request(
        SPLUNK_HEC_URL,
        data=payload.encode(),
        headers={
            "Authorization": f"Splunk {HEC_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            result = json.loads(resp.read())
            if result.get("code") != 0:
                print(f"  HEC error: {result}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"  HEC request failed: {e}", file=sys.stderr)
        return False
    return True


def load_json(filename):
    path = os.path.join(MOCK_DIR, filename)
    with open(path) as f:
        return json.load(f)


def seed_incidents():
    """Push incidents to index=incidents."""
    data = load_json("incidents.json")
    events = []
    for item in data:
        epoch = iso_to_epoch(item.get("_time"))
        events.append({
            "index": "incidents",
            "sourcetype": "soc_incidents",
            "host": "soc-es",
            "time": epoch,
            "event": item,
        })
    ok = send_events(events)
    print(f"  incidents: {len(events)} events -> {'OK' if ok else 'FAIL'}")


def seed_alerts():
    """Push alerts to index=alerts."""
    data = load_json("alerts.json")
    events = []
    for item in data:
        epoch = iso_to_epoch(item.get("_time"))
        events.append({
            "index": "alerts",
            "sourcetype": "soc_alerts",
            "host": "soc-es",
            "time": epoch,
            "event": item,
        })
    ok = send_events(events)
    print(f"  alerts: {len(events)} events -> {'OK' if ok else 'FAIL'}")


def seed_sla():
    """Push SLA metrics to index=sla."""
    data = load_json("sla-metrics.json")
    events = []
    for item in data:
        # SLA periods are weekly - use a synthetic timestamp (Monday of that week)
        period = item.get("period", "")
        if period.startswith("2026-W"):
            week_num = int(period.split("W")[1])
            dt = datetime.strptime(f"2026-W{week_num:02d}-1", "%G-W%V-%u")
            epoch = dt.timestamp()
        else:
            epoch = None
        events.append({
            "index": "sla",
            "sourcetype": "soc_sla",
            "host": "soc-es",
            "time": epoch,
            "event": item,
        })
    ok = send_events(events)
    print(f"  sla: {len(events)} events -> {'OK' if ok else 'FAIL'}")


def seed_soar():
    """Push playbook data to index=soar."""
    data = load_json("playbooks.json")
    events = []
    for item in data:
        epoch = iso_to_epoch(item.get("last_run_time"))
        events.append({
            "index": "soar",
            "sourcetype": "soc_playbooks",
            "host": "soar-server",
            "time": epoch,
            "event": item,
        })
    ok = send_events(events)
    print(f"  soar (playbooks): {len(events)} events -> {'OK' if ok else 'FAIL'}")


def seed_mitre():
    """Push MITRE coverage to index=mitre."""
    data = load_json("mitre-coverage.json")
    events = []
    now = datetime.now().timestamp()
    for item in data:
        events.append({
            "index": "mitre",
            "sourcetype": "soc_mitre",
            "host": "soc-es",
            "time": now,
            "event": item,
        })
    ok = send_events(events)
    print(f"  mitre: {len(events)} events -> {'OK' if ok else 'FAIL'}")


def seed_workload():
    """Push analyst workload to index=workload."""
    data = load_json("analyst-workload.json")
    events = []
    now = datetime.now().timestamp()
    for item in data:
        events.append({
            "index": "workload",
            "sourcetype": "soc_workload",
            "host": "soc-es",
            "time": now,
            "event": item,
        })
    ok = send_events(events)
    print(f"  workload: {len(events)} events -> {'OK' if ok else 'FAIL'}")


if __name__ == "__main__":
    print("Seeding Splunk with SOC mock data...")
    seed_incidents()
    seed_alerts()
    seed_sla()
    seed_soar()
    seed_mitre()
    seed_workload()
    print("Done.")
