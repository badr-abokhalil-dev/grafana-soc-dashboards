#!/usr/bin/env python3
"""
Move earliest_time/latest_time from URL query params to POST body form fields.

ROOT CAUSE: Splunk's /services/search/jobs/export ignores earliest_time/latest_time
when passed as URL query parameters. It ONLY respects them in the POST body.

This means Grafana's ${__from:date:seconds} substitution in the URL was useless -
the URL params were always ignored by Splunk.

FIX: Put earliest_time and latest_time in the POST body_form array:
  - Infinity DOES substitute variables in POST body form field values
  - Splunk DOES respect earliest_time/latest_time in POST body
  - This makes Grafana's time picker actually filter Splunk data

Changes per query:
  URL:  remove earliest_time/latest_time params
  Body: add earliest_time and latest_time form fields with ${__from:date:seconds}/${__to:date:seconds}
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

            url_options = target.get('url_options', {})
            body_form = url_options.get('body_form', [])
            if not body_form:
                continue

            # 1. Remove earliest_time/latest_time from URL
            new_url = url
            for param in [
                'earliest_time=${__from:date:seconds}&latest_time=${__to:date:seconds}',
                'earliest_time=${__from}&latest_time=${__to}',
                'earliest_time=${__from_ms}&latest_time=${__to_ms}',
            ]:
                new_url = new_url.replace('?' + param, '?')
                new_url = new_url.replace('&' + param, '')
                new_url = new_url.replace(param, '')

            # Clean up ?& and && and trailing ?/&
            while '?&' in new_url:
                new_url = new_url.replace('?&', '?')
            while '&&' in new_url:
                new_url = new_url.replace('&&', '&')
            new_url = new_url.rstrip('?&/')

            if new_url != url:
                target['url'] = new_url
                changed += 1

            # 2. Add earliest_time/latest_time to body_form
            # Check if they're already there
            keys_in_body = {item.get('key') for item in body_form}
            if 'earliest_time' not in keys_in_body:
                body_form.append({
                    'key': 'earliest_time',
                    'value': '${__from:date:seconds}'
                })
                changed += 1
            if 'latest_time' not in keys_in_body:
                body_form.append({
                    'key': 'latest_time',
                    'value': '${__to:date:seconds}'
                })
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
