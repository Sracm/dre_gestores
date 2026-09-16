import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'

with zipfile.ZipFile(path, 'r') as z:
    pages_json = json.loads(z.read('Report/definition/pages/pages.json').decode('utf-8'))
    for pid in pages_json.get('pageOrder', []):
        pdata = json.loads(z.read(f'Report/definition/pages/{pid}/page.json').decode('utf-8'))
        pname = pdata.get('displayName')
        print(f"\n==========================================")
        print(f"PAGE {pid}: {pname}")
        print(f"==========================================")
        
        for name in z.namelist():
            if name.startswith(f'Report/definition/pages/{pid}/visuals/') and name.endswith('.json'):
                vdata = json.loads(z.read(name).decode('utf-8'))
                v = vdata.get('visual', {})
                vtype = v.get('visualType')
                qs = v.get('query', {}).get('queryState', {})
                
                rows_proj = [p.get('queryRef') for p in qs.get('Rows', {}).get('projections', [])]
                cols_proj = [p.get('queryRef') for p in qs.get('Columns', {}).get('projections', [])]
                vals_proj = [p.get('queryRef') for p in qs.get('Values', {}).get('projections', [])]
                cat_proj  = [p.get('queryRef') for p in qs.get('Category', {}).get('projections', [])]
                y_proj    = [p.get('queryRef') for p in qs.get('Y', {}).get('projections', [])]
                
                print(f" - [{vtype}]")
                if rows_proj: print(f"    Rows: {rows_proj}")
                if cols_proj: print(f"    Cols: {cols_proj}")
                if vals_proj: print(f"    Vals: {vals_proj}")
                if cat_proj:  print(f"    Category: {cat_proj}")
                if y_proj:    print(f"    Y: {y_proj}")
