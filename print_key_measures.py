with open("all_measures_clean.txt", "r", encoding="utf-8") as f:
    text = f.read()

parts = text.split("==========================================")
targets = ["realizado", "orcado", "orçado", "antonio", "vb", "r/o", "margem"]

with open("key_measures_out.txt", "w", encoding="utf-8") as out:
    for p in parts:
        header = p.split("\n")[1] if len(p.split("\n")) > 1 else ""
        if any(t in header.lower() for t in targets):
            out.write("==========================================\n")
            out.write(p.strip() + "\n")

print("Wrote key_measures_out.txt successfully!")
