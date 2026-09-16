import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'
name = 'Report/definition/pages/2874193a146931f82491/visuals/9a77cda5593eb692a662/visual.json'

with zipfile.ZipFile(path, 'r') as z:
    data = json.loads(z.read(name).decode('utf-8'))
    v = data.get('visual', {})
    print("Visual Type:", v.get('visualType'))
    print("Objects:")
    for k, val in v.get('objects', {}).items():
        print(f"  {k}: {json.dumps(val, indent=2)[:300]}...")
