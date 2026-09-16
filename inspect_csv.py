import os

csv_path = "dre_cube_data.csv"
print(f"File size: {os.path.getsize(csv_path) / (1024*1024):.2f} MB")

with open(csv_path, "r", encoding="utf-8") as f:
    header = f.readline().strip().split("\t")
    print("Header columns:", header)
    for i in range(5):
        line = f.readline().strip().split("\t")
        print(f"Row {i}:", line)
