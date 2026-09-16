import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'

with zipfile.ZipFile(path, 'r') as z:
    for name in z.namelist():
        if name.endswith('.json'):
            try:
                content = json.loads(z.read(name).decode('utf-8'))
                
                # Check for filters
                def search_filters(obj, prefix=""):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k.lower() in ['filter', 'filters', 'where', 'slicer', 'selection', 'selected', 'defaultvalue']:
                                if v:
                                    print(f"[{name}] {prefix}.{k}: {json.dumps(v)[:300]}")
                            search_filters(v, f"{prefix}.{k}")
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            search_filters(item, f"{prefix}[{i}]")
                            
                search_filters(content)
            except Exception as e:
                pass
