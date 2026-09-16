import oracledb
from etl import config
conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
cur = conn.cursor()
try:
    cur.execute("SELECT SANKHYA.F_OBTEM_IMPOSTOSITE(1, 1) FROM DUAL")
    print("F_OBTEM_IMPOSTOSITE funcionou!")
except Exception as e:
    print("Erro F_OBTEM_IMPOSTOSITE:", e)
conn.close()
