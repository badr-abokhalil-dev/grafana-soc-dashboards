#!/usr/bin/env python3
"""Migrate Grafana dashboard panels from mock-server to Splunk queries."""

import json
import os
import copy

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DASHBOARD_DIR = os.path.join(BASE_DIR, "grafana", "dashboards")
SPLUNK_EXPORT_URL = "http://soc-splunk:8089/services/search/jobs/export?output_mode=csv&earliest_time=0&latest_time=now"

# Map mock-server URL patterns to Splunk indexes
URL_TO_INDEX = {
    "incidents": "incidents",
    "alerts": "alerts",
    "sla-metrics": "sla",
    "playbooks": "soar",
    "mitre-coverage": "mitre",
    "analyst-workload": "workload",
}


def detect_index(url):
    """Detect which Splunk index to use based on mock URL."""
    for pattern, index in URL_TO_INDEX.items():
        if pattern in url:
            return index
    return None


def build_spl(index, columns):
    """Build SPL query from index and column selectors."""
    fields = [col["selector"] for col in columns if col.get("selector")]
    table_clause = " ".join(fields)
    return f"search index={index} | table {table_clause}"


def transform_target(target):
    """Transform a single Infinity target from mock to Splunk."""
    url = target.get("url", "")
    if "soc-mock-server" not in url:
        return target

    index = detect_index(url)
    if not index:
        print(f"  WARNING: Could not detect index for URL: {url}")
        return target

    columns = target.get("columns", [])
    spl = build_spl(index, columns)

    new_target = copy.deepcopy(target)
    new_target["datasource"] = {"uid": "splunk-api"}
    new_target["type"] = "csv"
    new_target["url"] = SPLUNK_EXPORT_URL
    new_target["url_options"] = {
        "method": "POST",
        "body_type": "x-www-form-urlencoded",
        "body_form": [
            {"key": "search", "value": spl}
        ]
    }
    return new_target


def transform_panel(panel):
    """Transform all targets in a panel."""
    if "targets" in panel:
        panel["targets"] = [transform_target(t) for t in panel["targets"]]
    # Update panel-level datasource if it references mock-data
    if panel.get("datasource", {}).get("uid") == "mock-data":
        panel["datasource"] = {"uid": "splunk-api"}
    return panel


def transform_dashboard(filepath):
    """Transform an entire dashboard file."""
    with open(filepath) as f:
        dashboard = json.load(f)

    panel_count = 0
    for panel in dashboard.get("panels", []):
        if panel.get("datasource", {}).get("uid") == "mock-data" or \
           any("soc-mock-server" in t.get("url", "") for t in panel.get("targets", [])):
            transform_panel(panel)
            panel_count += 1

    with open(filepath, "w") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"  {os.path.basename(filepath)}: {panel_count} panels migrated")


if __name__ == "__main__":
    print("Migrating dashboards from mock-server to Splunk...")

    dashboards = [
        os.path.join(DASHBOARD_DIR, "management", "soc-overview.json"),
        os.path.join(DASHBOARD_DIR, "detailed", "incident-drilldown.json"),
        os.path.join(DASHBOARD_DIR, "detailed", "alert-analysis.json"),
        os.path.join(DASHBOARD_DIR, "detailed", "soar-drilldown.json"),
    ]

    for path in dashboards:
        if os.path.exists(path):
            transform_dashboard(path)
        else:
            print(f"  SKIP: {path} not found")

    # Also update provisioning copies
    prov_dir = os.path.join(BASE_DIR, "grafana", "provisioning", "dashboards")
    prov_files = [
        "soc-overview.json",
        "incident-drilldown.json",
        "alert-analysis.json",
        "soar-drilldown.json",
    ]
    for fname in prov_files:
        prov_path = os.path.join(prov_dir, fname)
        if os.path.exists(prov_path):
            transform_dashboard(prov_path)

    print("Done.")
