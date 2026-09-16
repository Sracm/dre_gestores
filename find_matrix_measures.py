with open("all_measures_clean.txt", "r", encoding="utf-8") as f:
    text = f.read()

parts = text.split("==========================================")
targets = ["realizado (r$) teste.", "teste antonio 2"]

with open("matrix_measures_clean.txt", "w", encoding="utf-8") as out:
    for p in parts:
        lines = [l for l in p.strip().split("\n") if l.strip()]
        if lines:
            header = lines[0]
            for t in targets:
                if t in header.lower():
                    out.write("==========================================\n")
                    out.write(p.strip() + "\n\n")

print("Saved matrix_measures_clean.txt")
