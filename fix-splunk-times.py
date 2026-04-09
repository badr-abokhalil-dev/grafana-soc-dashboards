#!/usr/bin/env python3
"""Fix Infinity plugin time variable interpolation in dashboard JSON files.

Problem: ${__from_ms}/${__to_ms} and ${__from:date:epoch}/${__to:date:epoch} are not
resolved by the Infinity backend (v3.8.0) → Splunk gets garbage → 500 HTML error.

Fix: Embed time range as Splunk inline search modifiers: earliest=-1w latest=now
This puts the time range INSIDE the search query string where Infinity doesn't
need to resolve template variables.

All dashboards use time: { from: "now-7d", to: "now" } so -1w/latest=now is correct.
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
                    # Remove any existing earliest/latest from search string
                    # (they shouldn't be there, but just in case)
                    search_lines = []
                    for part in search_value.split('|'):
                        part = part.strip()
                        if 'earliest=' in part or 'latest=' in part:
                            continue
                        search_lines.append(part)
                    base_search = ' | '.join(search_lines)

                    # Inject time range inline in search string
                    new_search = f"search {base_search} earliest=-1w latest=now"
                    if search_value != new_search:
                        item['value'] = new_search
                        changed += 1

            # Remove earliest_time/latest_time from URL query string
            # (no longer needed since time is in search string)
            new_url = url
            for param in ['earliest_time=${__from:date:epoch}&latest_time=${__to:date:epoch}',
                          'earliest_time=${__from_ms}&latest_time=${__to_ms}']:
                new_url = new_url.replace(param + '&', '')
                new_url = new_url.replace(param, '')

            # Clean up leftover ? and & in URL
            new_url = new_url.replace('?&', '?').replace('&&', '&')
            new_url = new_url.rstrip('?&')

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
