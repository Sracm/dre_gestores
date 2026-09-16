import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'

with zipfile.ZipFile(path, 'r') as z:
    for name in z.namelist():
        if 'bookmark' in name.lower():
            raw = z.read(name).decode('utf-8')
            bdata = json.loads(raw)
            print("====================================")
            print("BOOKMARK NAME:", name)
            sec = bdata.get('explorationState', {}).get('sections', {})
            for sec_id, sval in sec.items():
                print("SECTION:", sec_id)
                vc = sval.get('visualContainers', {})
                for v_id, v_val in vc.items():
                    filters = v_val.get('filters', {})
                    if filters:
                        print(f"  VISUAL {v_id} FILTERS:")
                        for item in filters.get('byExpr', []):
                            expr = item.get('expression', {})
                            fil = item.get('filter', {})
                            print(f"    - name: {item.get('name')}")
                            print(f"      expression: {expr}")
                            if fil:
                                print(f"      filter: {json.dumps(fil)}")
                    # check slicer state
                    so = v_val.get('singleVisual', {}).get('objects', {})
                    if so:
                        print(f"  VISUAL {v_id} OBJECTS: {list(so.keys())}")
                        gen = so.get('general') or so.get('merge', {}).get('general')
                        if gen:
                            print(f"    general: {json.dumps(gen)}")
