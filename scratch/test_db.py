import oracledb
from etl import config
conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
cur = conn.cursor()
try:
    cur.execute("SELECT COUNT(*) FROM SANKHYA.VMQ_DREQLIK WHERE ROWNUM = 1")
    print("Acesso direto a SANKHYA.VMQ_DREQLIK funcionou!")
except Exception as e:
    print("Erro no acesso direto:", e)
conn.close()
