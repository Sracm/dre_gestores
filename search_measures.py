with open("pbi_measures_all.txt", "r", encoding="utf-8") as f:
    text = f.read()

measures = text.split("----------------------------------")
for m in measures:
    if any(k in m.lower() for k in ["realizado", "orcado", "orçado", "antonio", "vb real"]):
        print("==================================")
        print(m.strip())
