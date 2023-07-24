#!/usr/bin/env python3

import json 
import glob
import uuid

dashboard_files = glob.glob('roles/grafana/files/panels/*.json')
fix_count = 0
print("Total dashboard files :", len(dashboard_files))
for db in dashboard_files:
    with open(db,'r+') as f:
        data = f.read()

        js = json.loads(data)
        if len(js['uid']) == 9:
            new_uuid = uuid.uuid4()
            print(f"need to add {new_uuid} to {db}")
            fix_count += 1
            js['uid'] = str(new_uuid)
            f.seek(0) 
            f.write(json.dumps(js, indent=2))
            f.truncate()

print("Total fixes: ", fix_count)

