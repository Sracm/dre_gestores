import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'
page_id = '2874193a146931f82491'

with zipfile.ZipFile(path, 'r') as z:
    pdata = json.loads(z.read(f'Report/definition/pages/{page_id}/page.json').decode('utf-8'))
    print('PAGE WIDTH:', pdata.get('width'), 'HEIGHT:', pdata.get('height'))
    
    visuals = []
    for name in z.namelist():
        if name.startswith(f'Report/definition/pages/{page_id}/visuals/') and name.endswith('.json'):
            vdata = json.loads(z.read(name).decode('utf-8'))
            pos = vdata.get('position', {})
            v = vdata.get('visual', {})
            vtype = v.get('visualType')
            
            # Check title
            title = ''
            for t_src in [v.get('objects', {}).get('title', []), vdata.get('visualContainerObjects', {}).get('title', [])]:
                if t_src:
                    t_props = t_src[0].get('properties', {})
                    if 'text' in t_props:
                        title = t_props['text'].get('expr', {}).get('Literal', {}).get('Value', '')
            
            visuals.append({
                'id': vdata.get('name'),
                'type': vtype,
                'x': pos.get('x'), 'y': pos.get('y'), 'w': pos.get('width'), 'h': pos.get('height'),
                'z': pos.get('z'),
                'title': title
            })
            
    visuals.sort(key=lambda x: (x['y'] or 0, x['x'] or 0))
    for vis in visuals:
        print(f"y={vis['y']:<5} x={vis['x']:<5} w={vis['w']:<5} h={vis['h']:<5} type={vis['type']:<30} title={vis['title']}")
