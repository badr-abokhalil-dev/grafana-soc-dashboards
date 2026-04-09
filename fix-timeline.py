#!/usr/bin/env python3
"""
Fix timeline: remove hardcoded earliest_time/latest_time from URL.
Use Grafana's built-in __from/__to variable substitution via URL params,
but in a format Splunk's export endpoint accepts.

Infinity plugin can substitute ${__from} and ${__to} as URL query params
(these are raw Grafana variables like 'now-7d', 'now').

We put the time params in the URL as literal Grafana variable tokens:
  ?earliest_time=${__from}&latest_time=${__to}

This way Grafana resolves them to the user's selected time range before
sending to Splunk.
"""

import json
import glob
import os

def fix_dashboard(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    changed = 0
    for panel in data.get('panels', []):
        for target in panel.get('targets', []):
            url = target.get('url', '')
            if 'soc-splunk' not in url:
                continue

            # Replace hardcoded time with Grafana variable tokens
            new_url = url.replace(
                'earliest_time=-1w&latest_time=now',
                'earliest_time=${__from}&latest_time=${__to}'
            )
            new_url = new_url.replace(
                'earliest_time=${__from_ms}&latest_time=${__to_ms}',
                'earliest_time=${__from}&latest_time=${__to}'
            )

            if new_url != url:
                target['url'] = new_url
                changed += 1

    if changed:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Fixed {filepath} ({changed} changes)")
    else:
        print(f"⏭️  No changes in {filepath}")

if __name__ == '__main__':
    base = '/home/abokhalil/.openclaw/workspace/projects/soc-dashboard/grafana/dashboards'
    for pattern in ['management/*.json', 'detailed/*.json']:
        for filepath in glob.glob(os.path.join(base, pattern)):
            fix_dashboard(filepath)
