import zipfile, json

path = r'C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ.2.1 - RH.pbix'

with zipfile.ZipFile(path, 'r') as z:
    for name in z.namelist():
        if name.startswith('Report/definition/bookmarks/'):
            print("BOOKMARK FILE:", name)
            try:
                raw = z.read(name).decode('utf-8')
                b = json.loads(raw)
                print("  Name:", b.get('displayName'), b.get('name'))
                # print any filters inside
                txt = json.dumps(b)
                for term in ['set', 'ago', 'jul', '2026', '9010000', 'RH']:
                    if term in txt.lower():
                        print(f"  Contains term '{term}'")
            except:
                pass
