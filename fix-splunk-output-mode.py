#!/usr/bin/env python3
"""
Fix SOC dashboard queries: switch from NDJSON (output_mode=json) to JSON array
(output_mode=json_rows) which returns a single parseable JSON object.

Infinity plugin's backend parser chokes on NDJSON multi-line responses.
json_rows format: {"fields": [...], "rows": [[...], [...]]} — single valid JSON.

Changes:
1. URL: output_mode=json → output_mode=json_rows
2. root_selector: "" → "rows"
3. columns: keep field-name selectors (Infinity resolves them against the fields array)
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
            if 'soc-splunk' not in url or 'output_mode=json' not in url:
                continue

            # 1. Change output_mode in URL
            new_url = url.replace('output_mode=json', 'output_mode=json_rows')
            if new_url != url:
                target['url'] = new_url
                changed += 1

            # 2. Fix root_selector — NDJSON uses "", json_rows needs "rows"
            if target.get('root_selector', '') == '':
                # Only change for json_rows queries (non-empty url_options.search body)
                has_search = any(
                    item.get('key') == 'search'
                    for item in target.get('url_options', {}).get('body_form', [])
                )
                if has_search:
                    target['root_selector'] = 'rows'
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
