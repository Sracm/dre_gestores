import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'
page_id = '2874193a146931f82491'

with zipfile.ZipFile(path, 'r') as z:
    for name in z.namelist():
        if f'pages/{page_id}/visuals/' in name and name.endswith('/visual.json'):
            raw = z.read(name).decode('utf-8')
            vdata = json.loads(raw)
            v = vdata.get('visual', {})
            if v.get('visualType') == 'slicer':
                print("SLICER:", vdata.get('name'))
                print("  Filter:", json.dumps(v.get('filter'), indent=2))
                print("  QueryState:", json.dumps(v.get('query', {}).get('queryState'), indent=2))
