import subprocess
import sqlite3
import time
import os

t0 = time.time()

# Connect to sqlite to get all distinct codcencus from dre_data
conn_lite = sqlite3.connect('dre_cache.db')
cur_lite = conn_lite.cursor()
cur_lite.execute("SELECT DISTINCT codcencus FROM dre_data WHERE codcencus > 0 ORDER BY codcencus")
all_centros = [r[0] for r in cur_lite.fetchall()]
conn_lite.close()

print(f"Total distinct centros: {len(all_centros)}")

# Prioritize Regional FSP and RH centros first!
priority_centros = [1020000, 1010200, 1010300, 1010400, 9010000, 1010100, 1010500]
other_centros = [c for c in all_centros if c not in priority_centros]
ordered_centros = priority_centros + other_centros

print(f"Priority centros: {priority_centros}")
