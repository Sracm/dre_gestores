"""
Script de sincronização da tabela Acessos_Usuario_CR no MariaDB.
Lê o matriz_acessos.json e garante que a tabela esteja 100% atualizada.
"""
import os
import json
import pymysql

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIZ_JSON = os.path.join(BASE_DIR, "matriz_acessos.json")

def seed():
    with open(MATRIZ_JSON, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for db_name in ["dre_gestores", "intranet"]:
        print(f"[*] Sincronizando {db_name}...")
        conn = pymysql.connect(
            host=os.getenv("MARIADB_HOST", "192.168.1.22"),
            user=os.getenv("MARIADB_USER", "antonio"),
            password=os.getenv("MARIADB_PASSWORD", "yzmpq100"),
            database=db_name,
            port=3306
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Acessos_Usuario_CR (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(100) NOT NULL,
                codcencus INT NOT NULL,
                centro_resultado VARCHAR(255) NOT NULL,
                canal VARCHAR(100) NOT NULL,
                ativo TINYINT(1) DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_usuario_cr (usuario, codcencus),
                INDEX idx_usuario (usuario),
                INDEX idx_codcencus (codcencus)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        insert_sql = """
            INSERT INTO Acessos_Usuario_CR (usuario, codcencus, centro_resultado, canal, ativo)
            VALUES (%s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                centro_resultado = VALUES(centro_resultado),
                canal = VALUES(canal),
                ativo = 1
        """
        batch = [(r["usuario"], r["codcencus"], r["centro_resultado"], r["canal"]) for r in dados]
        cur.executemany(insert_sql, batch)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM Acessos_Usuario_CR WHERE ativo = 1")
        print(f"[OK] {db_name}: {cur.fetchone()[0]} vínculos ativos.")
        conn.close()

if __name__ == "__main__":
    seed()
