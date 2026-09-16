import oracledb
from etl import config
conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
cur = conn.cursor()
cur.execute("SELECT text FROM all_views WHERE owner = 'SANKHYA' AND view_name = 'VMQ_DREQLIK'")
texto = cur.fetchone()[0]
if hasattr(texto, 'read'):
    texto = texto.read()

import re
# Vamos imprimir o texto para ver quais tabelas são usadas.
print(texto[:500])
with open("scratch/view_text.txt", "w") as f:
    f.write(texto)
