with open("all_measures_clean.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "MEASURE:" in line:
            print(line.strip())
