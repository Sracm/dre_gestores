"""Atualiza o dre_cache.db direto do Oracle.

Uso:
    python -m etl.atualizar_dados                  # incremental (janela padrão)
    python -m etl.atualizar_dados --desde 2024-01  # recarga completa a partir do mês
    python -m etl.atualizar_dados --forcar         # ignora a trava de validação

Fluxo: extrai do Oracle -> monta tabelas temporárias -> aplica as regras das
medidas DAX (REALIZADO (R$).. / ORÇADO (R$).) -> valida -> substitui os meses
da janela numa única transação. O app continua lendo durante a carga (WAL).
"""
import argparse
import datetime as dt
import logging
import os
import sqlite3
import sys
import time
from logging.handlers import RotatingFileHandler

from . import config, oracle_fonte

log = logging.getLogger("etl_dre")

NOMES_MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
LOCK_PATH = config.DB_PATH + ".etl.lock"
LOCK_EXPIRA_SEG = 2 * 3600


class ValidacaoError(RuntimeError):
    pass


# ═══════════════════════════════════════════════════════════════════════════
#  Infra
# ═══════════════════════════════════════════════════════════════════════════
def configurar_log():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    arq = RotatingFileHandler(os.path.join(config.LOG_DIR, "etl_dre.log"),
                              maxBytes=5 * 1024 * 1024, backupCount=10, encoding="utf-8")
    arq.setFormatter(fmt)
    tela = logging.StreamHandler(sys.stdout)
    tela.setFormatter(fmt)
    log.setLevel(logging.INFO)
    log.handlers = [arq, tela]


def adquirir_lock():
    if os.path.exists(LOCK_PATH) and time.time() - os.path.getmtime(LOCK_PATH) > LOCK_EXPIRA_SEG:
        log.warning("Lock expirado removido: %s", LOCK_PATH)
        os.remove(LOCK_PATH)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    return True


def liberar_lock():
    try:
        os.remove(LOCK_PATH)
    except FileNotFoundError:
        pass


def primeiro_dia(ano, mes):
    return dt.datetime(ano, mes, 1)


def somar_meses(d, n):
    total = d.year * 12 + (d.month - 1) + n
    return dt.datetime(total // 12, total % 12 + 1, 1)


def meses_entre(dt_ini, dt_fim):
    d = dt_ini
    while d < dt_fim:
        yield d
        d = somar_meses(d, 1)


# ═══════════════════════════════════════════════════════════════════════════
#  Esquema SQLite
# ═══════════════════════════════════════════════════════════════════════════
def preparar_banco(conn):
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS etl_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inicio TEXT NOT NULL,
            fim TEXT,
            modo TEXT,
            periodo_ini TEXT,
            periodo_fim TEXT,
            linhas_dre INTEGER,
            linhas_detalhe INTEGER,
            view_hash TEXT,
            status TEXT NOT NULL,
            erro TEXT
        );
        CREATE TABLE IF NOT EXISTS dre_data (
            ano INTEGER, mes INTEGER, trimestre TEXT, semestre TEXT, empresa TEXT,
            codcencus INTEGER, descrcencus TEXT, bloco TEXT, titulo TEXT, descrnat TEXT,
            orcado REAL, realizado REAL, vb_orcado REAL, vb_realizado REAL
        );
        CREATE TABLE IF NOT EXISTS dre_resumo_mensal (
            ano INT, mes INT, empresa TEXT, codcencus INT, bloco TEXT, realizado, orcado
        );
        CREATE TABLE IF NOT EXISTS dre_detalhe_rh (
            ano INTEGER, mes INTEGER, nomemes TEXT, tri_ano TEXT, bloco TEXT, titulo TEXT,
            descrnat TEXT, parceiro TEXT, orcado REAL, realizado REAL
        );
        CREATE TABLE IF NOT EXISTS dre_detalhe_fsp (
            ano INTEGER, mes INTEGER, nomemes TEXT, tri_ano TEXT, codcencus INTEGER,
            bloco TEXT, titulo TEXT, descrnat TEXT, parceiro TEXT, orcado REAL, realizado REAL
        );
        CREATE TABLE IF NOT EXISTS dre_filtros_anos (ano INT);
        CREATE TABLE IF NOT EXISTS dre_filtros_empresas (nome TEXT);
        CREATE TABLE IF NOT EXISTS dre_filtros_centros (codcencus INT, nome TEXT);
        CREATE INDEX IF NOT EXISTS idx_dre_combo ON dre_data(ano, mes, empresa, codcencus);
        CREATE INDEX IF NOT EXISTS idx_resumo_mensal ON dre_resumo_mensal(ano, empresa, codcencus);
        CREATE INDEX IF NOT EXISTS idx_dre_detalhe_rh_ano_mes ON dre_detalhe_rh(ano, mes);
        CREATE INDEX IF NOT EXISTS idx_dre_detalhe_fsp_ano_mes ON dre_detalhe_fsp(ano, mes);
        CREATE INDEX IF NOT EXISTS idx_dre_detalhe_fsp_cenc ON dre_detalhe_fsp(codcencus);
    """)


def registrar_inicio(conn, modo, dt_ini, dt_fim):
    cur = conn.execute(
        "INSERT INTO etl_status (inicio, modo, periodo_ini, periodo_fim, status) VALUES (?, ?, ?, ?, 'executando')",
        (dt.datetime.now().isoformat(timespec="seconds"), modo, dt_ini.date().isoformat(), dt_fim.date().isoformat()))
    conn.commit()
    return cur.lastrowid


# ═══════════════════════════════════════════════════════════════════════════
#  Staging + transformação
# ═══════════════════════════════════════════════════════════════════════════
def carregar_staging(conn, fatos, dims):
    conn.executescript("""
        DROP TABLE IF EXISTS temp.stg_fato;
        DROP TABLE IF EXISTS temp.stg_caddre;
        DROP TABLE IF EXISTS temp.stg_natureza;
        DROP TABLE IF EXISTS temp.stg_centro;
        DROP TABLE IF EXISTS temp.stg_empresa;
        DROP TABLE IF EXISTS temp.stg_parceiro;
        CREATE TEMP TABLE stg_fato (ano INT, mes INT, codemp INT, codcencus INT, codnat INT, ref TEXT,
                                    codparc INT, valor REAL, orcamento REAL);
        CREATE TEMP TABLE stg_caddre (codcencus INT, codnat INT, ref TEXT, bloco TEXT, titulo TEXT, fator REAL, refkey TEXT);
        CREATE TEMP TABLE stg_natureza (codnat INT PRIMARY KEY, descrnat TEXT);
        CREATE TEMP TABLE stg_centro (codcencus INT PRIMARY KEY, descrcencus TEXT);
        CREATE TEMP TABLE stg_empresa (codemp INT PRIMARY KEY, nome TEXT);
        CREATE TEMP TABLE stg_parceiro (codparc INT PRIMARY KEY, nome TEXT);
    """)
    conn.executemany("INSERT INTO stg_fato VALUES (?,?,?,?,?,?,?,?,?)", fatos)

    nat_bonif = set(config.NATUREZAS_BONIF)
    conn.executemany(
        "INSERT INTO stg_caddre VALUES (?,?,?,?,?,?,?)",
        [(c, n, r, b, t, f, "CUSTOGER" if (n in nat_bonif and r == "VALORNF") else r)
         for (c, n, r, b, t, f) in dims["caddre"]])
    conn.executemany("INSERT OR REPLACE INTO stg_natureza VALUES (?,?)", dims["natureza"])
    conn.executemany("INSERT OR REPLACE INTO stg_centro VALUES (?,?)", dims["centro"])
    conn.executemany("INSERT OR REPLACE INTO stg_empresa VALUES (?,?)", dims["empresa"])
    conn.executemany("INSERT OR REPLACE INTO stg_parceiro VALUES (?,?)", dims["parceiro"])
    conn.execute("CREATE INDEX temp.idx_stg_caddre ON stg_caddre(codcencus, codnat, refkey)")

    dup = conn.execute("""SELECT COUNT(*) FROM (SELECT 1 FROM stg_caddre
                          GROUP BY codcencus, codnat, refkey HAVING COUNT(*) > 1)""").fetchone()[0]
    if dup:
        raise ValidacaoError(f"VMQ_CADDRE com {dup} chaves duplicadas (quebraria o relacionamento do modelo)")


# Fatos ligados à VMQ_CADDRE pela "chave bonif2" e valor realizado já calculado
# conforme REALIZADO (R$).. : bonificação usa valor10 só de REF=VALORNF,
# demais títulos usam VLR. = VALOR * FATOR.
_SQL_BASE = """
    CREATE TEMP TABLE stg_base AS
    SELECT f.ano, f.mes, f.codemp, f.codcencus, f.codnat, f.codparc, c.bloco, c.titulo,
           SUM(CASE
                 WHEN c.titulo = :titulo_bonif THEN
                   CASE WHEN f.ref = 'VALORNF' THEN f.valor *
                        CASE WHEN f.codnat = 12010301 THEN -1
                             WHEN f.codnat = 12010302 THEN 1
                             ELSE c.fator END
                        ELSE 0 END
                 ELSE f.valor * c.fator
               END) AS realizado,
           SUM(f.orcamento) AS orcado
      FROM stg_fato f
      JOIN stg_caddre c
        ON c.codcencus = f.codcencus
       AND c.codnat = f.codnat
       AND c.refkey = CASE WHEN f.codnat IN (12010301, 12010302) AND f.ref = 'VALORNF'
                           THEN 'CUSTOGER' ELSE f.ref END
     GROUP BY f.ano, f.mes, f.codemp, f.codcencus, f.codnat, f.codparc, c.bloco, c.titulo
"""

# ORÇADO (R$). no bloco 3 soma o orçado da bonificação da mesma natureza/contexto
# (exceto no título de impostos s/ bonificações); fora do bloco 3 a bonificação dobra.
_ORCADO_FINAL = """
    CASE
      WHEN bloco = :bloco_desp_vendas THEN
        CASE WHEN titulo = :titulo_impostos_bonif THEN orcado
             ELSE orcado + SUM(CASE WHEN titulo = :titulo_bonif THEN orcado ELSE 0 END)
                           OVER (PARTITION BY {particao})
        END
      WHEN titulo = :titulo_bonif THEN orcado * 2
      ELSE orcado
    END
"""


def _in_nomeado(prefixo, valores, params):
    nomes = []
    for i, v in enumerate(valores):
        params[f"{prefixo}{i}"] = v
        nomes.append(f":{prefixo}{i}")
    return ",".join(nomes)


def transformar(conn):
    params = {
        "titulo_bonif": config.TITULO_BONIF,
        "titulo_impostos_bonif": config.TITULO_IMPOSTOS_BONIF,
        "bloco_desp_vendas": config.BLOCO_DESP_VENDAS,
    }
    conn.execute("DROP TABLE IF EXISTS temp.stg_base")
    conn.execute(_SQL_BASE, {"titulo_bonif": config.TITULO_BONIF})

    p_dre = dict(params)
    blocos_in = _in_nomeado("bloco", config.BLOCOS_DRE, p_dre)
    conn.execute("DROP TABLE IF EXISTS temp.stg_dre")
    conn.execute(f"""
        CREATE TEMP TABLE stg_dre AS
        WITH agg AS (
            SELECT b.ano, b.mes, e.nome AS empresa, b.codcencus, COALESCE(ce.descrcencus, '') AS descrcencus,
                   b.bloco, b.titulo, COALESCE(n.descrnat, '') AS descrnat,
                   SUM(b.realizado) AS realizado, SUM(b.orcado) AS orcado
              FROM stg_base b
              JOIN stg_empresa e ON e.codemp = b.codemp
              LEFT JOIN stg_natureza n ON n.codnat = b.codnat
              LEFT JOIN stg_centro ce ON ce.codcencus = b.codcencus
             WHERE b.bloco IN ({blocos_in})
             GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
        )
        SELECT ano, mes,
               'T' || ((mes + 2) / 3) AS trimestre,
               CASE WHEN mes < 7 THEN '1º Sem.' ELSE '2º Sem.' END AS semestre,
               empresa, codcencus, descrcencus, bloco, titulo, descrnat,
               {_ORCADO_FINAL.format(particao="ano, mes, empresa, codcencus, bloco, descrnat")} AS orcado,
               realizado,
               0.0 AS vb_orcado, 0.0 AS vb_realizado
          FROM agg
    """, p_dre)
    conn.execute("DELETE FROM stg_dre WHERE ABS(orcado) < 0.005 AND ABS(realizado) < 0.005")

    p_det = dict(params)
    centros_in = _in_nomeado("cenc", config.CENTROS_DETALHE_PARCEIRO, p_det)
    conn.execute("DROP TABLE IF EXISTS temp.stg_detalhe")
    conn.execute(f"""
        CREATE TEMP TABLE stg_detalhe AS
        WITH agg AS (
            SELECT b.ano, b.mes, b.bloco, b.titulo, COALESCE(n.descrnat, '') AS descrnat,
                   COALESCE(p.nome, '') AS parceiro,
                   SUM(b.realizado) AS realizado, SUM(b.orcado) AS orcado
              FROM stg_base b
              LEFT JOIN stg_natureza n ON n.codnat = b.codnat
              LEFT JOIN stg_parceiro p ON p.codparc = b.codparc
             WHERE b.codcencus IN ({centros_in})
             GROUP BY 1, 2, 3, 4, 5, 6
        )
        SELECT ano, mes, '' AS nomemes, 'T' || ((mes + 2) / 3) || '-' || ano AS tri_ano,
               bloco, titulo, descrnat, parceiro,
               {_ORCADO_FINAL.format(particao="ano, mes, bloco, descrnat, parceiro")} AS orcado,
               realizado
          FROM agg
    """, p_det)
    conn.execute("DELETE FROM stg_detalhe WHERE ABS(orcado) < 0.005 AND ABS(realizado) < 0.005")
    conn.executemany("UPDATE stg_detalhe SET nomemes = ? WHERE mes = ?",
                     [(nome, i) for i, nome in enumerate(NOMES_MES, start=1)])

    conn.execute("DROP TABLE IF EXISTS temp.stg_detalhe_fsp")
    conn.execute(f"""
        CREATE TEMP TABLE stg_detalhe_fsp AS
        WITH agg AS (
            SELECT b.ano, b.mes, b.codcencus, b.bloco, b.titulo, COALESCE(n.descrnat, '') AS descrnat,
                   COALESCE(p.nome, '') AS parceiro,
                   SUM(b.realizado) AS realizado, SUM(b.orcado) AS orcado
              FROM stg_base b
              LEFT JOIN stg_natureza n ON n.codnat = b.codnat
              LEFT JOIN stg_parceiro p ON p.codparc = b.codparc
             GROUP BY 1, 2, 3, 4, 5, 6, 7
        )
        SELECT ano, mes, '' AS nomemes, 'T' || ((mes + 2) / 3) || '-' || ano AS tri_ano,
               codcencus, bloco, titulo, descrnat, parceiro,
               {_ORCADO_FINAL.format(particao="ano, mes, codcencus, bloco, descrnat, parceiro")} AS orcado,
               realizado
          FROM agg
    """, params)
    conn.execute("DELETE FROM stg_detalhe_fsp WHERE ABS(orcado) < 0.005 AND ABS(realizado) < 0.005")
    conn.executemany("UPDATE stg_detalhe_fsp SET nomemes = ? WHERE mes = ?",
                     [(nome, i) for i, nome in enumerate(NOMES_MES, start=1)])


# ═══════════════════════════════════════════════════════════════════════════
#  Validação e publicação
# ═══════════════════════════════════════════════════════════════════════════
def validar(conn, dt_ini, dt_fim, forcar):
    """Impede que uma extração incompleta apague dados bons.

    Para cada mês já passado da janela, compara o total absoluto novo com o
    publicado. Uma queda maior que a tolerância aborta a carga.
    """
    hoje = dt.datetime.now()
    mes_atual = primeiro_dia(hoje.year, hoje.month)
    problemas = []
    for d in meses_entre(dt_ini, min(dt_fim, mes_atual)):
        novo = conn.execute("SELECT COALESCE(SUM(ABS(realizado)),0) FROM stg_dre WHERE ano=? AND mes=?",
                            (d.year, d.month)).fetchone()[0]
        atual = conn.execute("SELECT COALESCE(SUM(ABS(realizado)),0) FROM main.dre_data WHERE ano=? AND mes=?",
                             (d.year, d.month)).fetchone()[0]
        if atual > 0 and novo < atual * (1 - config.VALIDACAO_TOLERANCIA):
            problemas.append(f"{d:%Y-%m}: realizado absoluto caiu de {atual:,.0f} para {novo:,.0f}")
    if problemas:
        msg = "; ".join(problemas)
        if forcar:
            log.warning("Validação ignorada (--forcar): %s", msg)
        else:
            raise ValidacaoError(msg)


def publicar(conn, dt_ini, dt_fim):
    faixa = "(ano * 100 + mes) >= ? AND (ano * 100 + mes) < ?"
    p = (dt_ini.year * 100 + dt_ini.month, dt_fim.year * 100 + dt_fim.month)
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(f"DELETE FROM main.dre_data WHERE {faixa}", p)
        conn.execute("INSERT INTO main.dre_data SELECT * FROM stg_dre")

        conn.execute(f"DELETE FROM main.dre_resumo_mensal WHERE {faixa}", p)
        conn.execute(f"""INSERT INTO main.dre_resumo_mensal
                         SELECT ano, mes, empresa, codcencus, bloco, SUM(realizado), SUM(orcado)
                           FROM stg_dre GROUP BY ano, mes, empresa, codcencus, bloco""")

        conn.execute(f"DELETE FROM main.dre_detalhe_rh WHERE {faixa}", p)
        conn.execute("INSERT INTO main.dre_detalhe_rh SELECT * FROM stg_detalhe")

        conn.execute(f"DELETE FROM main.dre_detalhe_fsp WHERE {faixa}", p)
        conn.execute("INSERT INTO main.dre_detalhe_fsp SELECT * FROM stg_detalhe_fsp")

        conn.execute("DELETE FROM main.dre_filtros_anos")
        conn.execute("INSERT INTO main.dre_filtros_anos SELECT DISTINCT ano FROM main.dre_data WHERE ano > 2000")
        conn.execute("DELETE FROM main.dre_filtros_empresas")
        conn.execute("INSERT INTO main.dre_filtros_empresas SELECT DISTINCT nome FROM stg_empresa WHERE nome <> ''")
        p_blocos = {}
        blocos_in = _in_nomeado("bloco", config.BLOCOS_DRE, p_blocos)
        conn.execute("DELETE FROM main.dre_filtros_centros")
        conn.execute(f"""INSERT INTO main.dre_filtros_centros
                         SELECT DISTINCT c.codcencus, ce.descrcencus
                           FROM stg_caddre c JOIN stg_centro ce ON ce.codcencus = c.codcencus
                          WHERE c.codcencus > 0 AND c.bloco IN ({blocos_in})""", p_blocos)
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


# ═══════════════════════════════════════════════════════════════════════════
#  Execução
# ═══════════════════════════════════════════════════════════════════════════
def calcular_janela(desde):
    hoje = dt.datetime.now()
    mes_atual = primeiro_dia(hoje.year, hoje.month)
    if desde:
        # Recarga completa: inclui o orçamento dos meses futuros do ano
        ano, mes = (int(x) for x in desde.split("-")[:2])
        return primeiro_dia(ano, mes), primeiro_dia(hoje.year + 1, 1), "completo"
    return somar_meses(mes_atual, -(config.MESES_ATUALIZAR - 1)), somar_meses(mes_atual, 1), "incremental"


def executar(desde=None, forcar=False):
    dt_ini, dt_fim, modo = calcular_janela(desde)
    t0 = time.time()
    conn = sqlite3.connect(config.DB_PATH, timeout=60, isolation_level=None)
    preparar_banco(conn)
    run_id = registrar_inicio(conn, modo, dt_ini, dt_fim)
    log.info("Início %s | janela %s a %s | banco %s", modo, dt_ini.date(), dt_fim.date(), config.DB_PATH)
    try:
        ora = oracle_fonte.conectar()
        fatos, view_hash = [], None
        # Os ramos financeiros da view (VGFFINRAT) fazem full scan em TGFFIN a cada
        # consulta, independentemente do período: uma consulta por ano, não por mês.
        d = dt_ini
        while d < dt_fim:
            ate = min(primeiro_dia(d.year + 1, 1), dt_fim)
            t = time.time()
            linhas, view_hash = oracle_fonte.extrair_fatos(ora, d, ate)
            fatos.extend(linhas)
            log.info("  Oracle %s a %s: %d linhas em %.1fs", f"{d:%Y-%m}", f"{ate:%Y-%m}", len(linhas), time.time() - t)
            d = ate
        dims = oracle_fonte.extrair_dimensoes(ora, [f[6] for f in fatos])
        ora.close()
        log.info("  Dimensões: %s", {k: len(v) for k, v in dims.items()})

        carregar_staging(conn, fatos, dims)
        transformar(conn)
        n_dre = conn.execute("SELECT COUNT(*) FROM stg_dre").fetchone()[0]
        n_det = conn.execute("SELECT COUNT(*) FROM stg_detalhe").fetchone()[0]
        validar(conn, dt_ini, dt_fim, forcar)
        publicar(conn, dt_ini, dt_fim)

        conn.execute("""UPDATE etl_status SET fim=?, status='sucesso', linhas_dre=?, linhas_detalhe=?, view_hash=?
                        WHERE id=?""",
                     (dt.datetime.now().isoformat(timespec="seconds"), n_dre, n_det, view_hash, run_id))
        log.info("Concluído: %d linhas DRE, %d linhas detalhe em %.1fs", n_dre, n_det, time.time() - t0)
        return 0
    except Exception as e:
        log.exception("Falha na atualização")
        conn.execute("UPDATE etl_status SET fim=?, status='erro', erro=? WHERE id=?",
                     (dt.datetime.now().isoformat(timespec="seconds"), f"{type(e).__name__}: {e}"[:2000], run_id))
        return 1
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description="Atualiza o cache do DRE Gestores a partir do Oracle")
    ap.add_argument("--desde", help="recarga completa a partir de AAAA-MM")
    ap.add_argument("--forcar", action="store_true", help="publica mesmo se a validação acusar queda")
    args = ap.parse_args()

    configurar_log()
    if not adquirir_lock():
        log.info("Outra atualização em andamento (%s); saindo.", LOCK_PATH)
        return 0
    try:
        return executar(args.desde, args.forcar)
    finally:
        liberar_lock()


if __name__ == "__main__":
    sys.exit(main())
