import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'

with zipfile.ZipFile(path, 'r') as z:
    raw = z.read('Report/definition/bookmarks/5bc0ec5a287d2feaab3e.bookmark.json').decode('utf-8')
    bdata = json.loads(raw)
    sec = bdata.get('explorationState', {}).get('sections', {})
    for sec_id, sval in sec.items():
        print("SECTION:", sec_id)
        vc = sval.get('visualContainers', {})
        for v_id, v_val in vc.items():
            so = v_val.get('singleVisual', {}).get('objects', {})
            if so:
                for k, v in so.items():
                    print(f"  Visual {v_id} [{k}]: {json.dumps(v)[:200]}")
