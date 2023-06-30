#!/usr/bin/env python3

import json 
import glob
# import uuid

dashboard_files = glob.glob('../roles/grafana/files/panels/*.json')
fix_count = 0

for db in dashboard_files:
    with open(db,'r+') as f:
        data = f.read()

        js = json.loads(data)
        name = js['name']

        uid = js['uid']
        lp = js['model'].get('libraryPanel')
        js['model']['libraryPanel'] = {
            "name": name,
            "uid": uid
        }
        f.seek(0)
        f.write(json.dumps(js, indent=2))
        f.truncate()
        print(f"updating {db}")
        fix_count += 1

print("Total dashboard files :", len(dashboard_files))
print("Total updates made :", fix_count)
