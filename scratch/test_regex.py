import oracledb
import re
from etl import config
conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
cur = conn.cursor()
with open("scratch/view_text.txt", "r") as f:
    text = f.read()

# Trocar nomes das tabelas colocando SANKHYA. na frente.
# Exemplo básico:
# FROM TGFCAB -> FROM SANKHYA.TGFCAB
# JOIN TGFITE -> JOIN SANKHYA.TGFITE
text = re.sub(r'\bFROM\s+([A-Z_]+)\b', r'FROM SANKHYA.\1', text, flags=re.IGNORECASE)
text = re.sub(r'\bJOIN\s+([A-Z_]+)\b', r'JOIN SANKHYA.\1', text, flags=re.IGNORECASE)

try:
    cur.execute(f"SELECT * FROM ({text}) WHERE ROWNUM = 1")
    print("Com SANKHYA. prepended, funcionou!")
except Exception as e:
    print("Erro com SANKHYA. prepended:", e)

conn.close()
