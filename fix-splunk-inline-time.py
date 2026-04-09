#!/usr/bin/env python3
"""
Remove inline earliest/latest from Splunk search strings and move them to URL params.

Problem: "search index=incidents | table ... earliest=-1w latest=now" returns empty
from Splunk's /services/search/jobs/export endpoint (CSV mode) — Splunk's export
handler doesn't parse inline time modifiers correctly.

Fix: Remove earliest=-1w latest=now from the search body string and add them
as URL query parameters instead:
  URL: ?output_mode=csv&earliest_time=-1w&latest_time=now
  Body: search index=incidents | table ...
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
            for item in body_form:
                if item.get('key') == 'search':
                    search_value = item['value']

                    # Remove inline earliest=/latest= from search string
                    import re
                    # Remove earliest=-Nd, earliest=-Nw, etc. and latest=now etc.
                    cleaned = re.sub(r'\s+earliest=[^\s|]+', '', search_value)
                    cleaned = re.sub(r'\s+latest_time=[^\s|]+', '', cleaned)
                    # Also handle latest= (without _time suffix)
                    cleaned = re.sub(r'\s+latest=[^\s|]+', '', cleaned)
                    cleaned = cleaned.strip()

                    if cleaned != search_value:
                        item['value'] = cleaned
                        changed += 1

            # Ensure earliest_time and latest_time are in URL
            has_time_params = 'earliest_time=' in url and 'latest_time=' in url
            if not has_time_params:
                sep = '&' if '?' in url else '?'
                new_url = f"{url}{sep}earliest_time=-1w&latest_time=now"
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
