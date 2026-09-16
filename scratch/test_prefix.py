import oracledb
from etl import config
conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
cur = conn.cursor()
try:
    cur.execute("SELECT COUNT(*) FROM SANKHYA.TGFCAB WHERE ROWNUM = 1")
    print("SANKHYA.TGFCAB funcionou!")
except Exception as e:
    print("Erro TGFCAB:", e)
    
try:
    cur.execute("SELECT COUNT(*) FROM SANKHYA.AD_ORCAMENTO WHERE ROWNUM = 1")
    print("SANKHYA.AD_ORCAMENTO funcionou!")
except Exception as e:
    print("Erro AD_ORCAMENTO:", e)

conn.close()
