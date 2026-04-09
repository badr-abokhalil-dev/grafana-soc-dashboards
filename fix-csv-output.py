#!/usr/bin/env python3
"""
Switch SOC dashboards from json/json_rows to CSV format.

Problem: Infinity plugin 3.8.0 backend parser fails to parse Splunk's NDJSON
(output_mode=json) or 2D-array json_rows (output_mode=json_rows) correctly.

Solution: Use output_mode=csv which Infinity parses natively and correctly.
The CSV header row provides field names; Infinity maps subsequent rows accordingly.

Changes per query:
1. URL: output_mode=json_rows → output_mode=csv
2. type: json → type: csv
3. root_selector: "rows" → "" (not needed for CSV)
4. columns: keep as-is (for field naming/type hints)
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

            # 1. Switch output_mode in URL
            if 'output_mode=json_rows' in url:
                new_url = url.replace('output_mode=json_rows', 'output_mode=csv')
                target['url'] = new_url
                changed += 1

            # 2. Change type from json to csv
            if target.get('type') == 'json':
                target['type'] = 'csv'
                changed += 1

            # 3. Reset root_selector (not needed for CSV)
            if target.get('root_selector') == 'rows':
                target['root_selector'] = ''
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
