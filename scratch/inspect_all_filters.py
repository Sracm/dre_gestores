import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'
page_id = '2874193a146931f82491'

with zipfile.ZipFile(path, 'r') as z:
    # 1. Report level filters
    if 'Report/definition/report.json' in z.namelist():
        rep = json.loads(z.read('Report/definition/report.json').decode('utf-8'))
        print("=== REPORT FILTERS ===")
        print(json.dumps(rep.get('filters'), indent=2))
        
    # 2. Page level filters
    if f'Report/definition/pages/{page_id}/page.json' in z.namelist():
        pdata = json.loads(z.read(f'Report/definition/pages/{page_id}/page.json').decode('utf-8'))
        print("=== PAGE FILTERS ===")
        print(json.dumps(pdata.get('filter'), indent=2))
        print("=== PAGE OBJECTS ===")
        print(json.dumps(pdata.get('objects'), indent=2))

    # 3. Visual level filters on the matrix
    vpath = f'Report/definition/pages/{page_id}/visuals/9a77cda5593eb692a662/visual.json'
    if vpath in z.namelist():
        vdata = json.loads(z.read(vpath).decode('utf-8'))
        print("=== MATRIX VISUAL FILTER ===")
        print(json.dumps(vdata.get('visual', {}).get('filter'), indent=2))
        print("=== MATRIX QUERY FILTERS ===")
        cmd = vdata.get('visual', {}).get('query', {}).get('Commands', [{}])[0]
        q = cmd.get('SemanticQueryDataShapeCommand', {}).get('Query', {})
        print(json.dumps(q.get('Where'), indent=2))
