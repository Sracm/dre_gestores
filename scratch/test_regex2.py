import oracledb
import re
from etl import config
conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
cur = conn.cursor()
with open("scratch/view_text.txt", "r") as f:
    text = f.read()

tabelas_e_funcs = [
    "TGFCAB", "TGFITE", "TGFTOP", "VGFCAB", "TGFVAR", "VGFFINRAT", "AD_FLUXODRE", "AD_ORCAMENTO",
    "F_OBTEM_IMPOSTOSITE", "F_OBTEM_CUSTO_MQ", "OBTEMCUSTO", "AD_CADDREDET"
]
for tab in tabelas_e_funcs:
    text = re.sub(rf'(?<!\.)\b{tab}\b', f'SANKHYA.{tab}', text, flags=re.IGNORECASE)

try:
    cur.execute(f"SELECT COUNT(*) FROM ({text}) WHERE ROWNUM = 1")
    print("Tudo resolvido!")
except Exception as e:
    print("Erro:", e)

conn.close()
