"""Extração direta do Oracle (Sankhya).

A VMQ_DREQLIK aplicada com filtro externo em DTCOMP não usa índice nos ramos
financeiros (DTCOMP é um CASE), o que gera full scan em TGFFIN. Por isso o texto
da view é lido do próprio Oracle e apenas os cortes de data são trocados por
binds nas colunas-base indexadas. Se a view mudar a ponto de os cortes não
serem encontrados, a extração aborta em vez de gravar dado incompleto.
"""
import hashlib
import oracledb
import re

from . import config

# (trecho original, trecho original + bind). O corte de 2024 da view é mantido.
# Comissões voltam 1 mês (DTCOMP = mês anterior ao DTNEG/DHBAIXA), então os
# ramos FIN buscam até 1 mês à frente e o filtro externo em DTCOMP recorta.
_CORTES = [
    ("AND CAB.DTENTSAI>=TO_DATE('01/01/2024','DD/MM/YYYY')",
     "AND CAB.DTENTSAI>=TO_DATE('01/01/2024','DD/MM/YYYY') AND CAB.DTENTSAI>=:dt_ini AND CAB.DTENTSAI<:dt_fim"),
    ("AND fin.dtneg>=TO_DATE('01/01/2024','DD/MM/YYYY')",
     "AND fin.dtneg>=TO_DATE('01/01/2024','DD/MM/YYYY') AND fin.dtneg>=:dt_ini AND fin.dtneg<ADD_MONTHS(:dt_fim,1)"),
    ("AND FIN.DHBAIXA>=TO_DATE('01/01/2024','DD/MM/YYYY')",
     "AND FIN.DHBAIXA>=TO_DATE('01/01/2024','DD/MM/YYYY') AND FIN.DHBAIXA>=:dt_ini AND FIN.DHBAIXA<ADD_MONTHS(:dt_fim,1)"),
    ("WHERE DTNEG>=TO_DATE('01/01/2024','DD/MM/YYYY')",
     "WHERE DTNEG>=TO_DATE('01/01/2024','DD/MM/YYYY') AND DTNEG>=:dt_ini AND DTNEG<:dt_fim"),
    ("FROM AD_ORCAMENTO\r\nWHERE CODCENCUS NOT IN (21010000)",
     "FROM AD_ORCAMENTO\r\nWHERE CODCENCUS NOT IN (21010000) AND DTREF>=:dt_ini AND DTREF<:dt_fim"),
]


class ViewAlteradaError(RuntimeError):
    pass


def conectar():
    if not config.ORACLE_PASSWORD:
        raise RuntimeError("ORACLE_PASSWORD não definido (configure o arquivo .env)")
    conn = oracledb.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
    with conn.cursor() as cur:
        cur.execute("ALTER SESSION SET CURRENT_SCHEMA = SANKHYA")
    return conn


def _sql_view_por_periodo(cur):
    cur.execute("SELECT text FROM all_views WHERE owner = 'SANKHYA' AND view_name = 'VMQ_DREQLIK'")
    texto = cur.fetchone()[0]
    if hasattr(texto, "read"):
        texto = texto.read()
    texto_norm = texto.replace("\r\n", "\n").replace("\n", "\r\n")
    for original, novo in _CORTES:
        if texto_norm.count(original) != 1:
            raise ViewAlteradaError(f"Corte de data não encontrado na VMQ_DREQLIK: {original!r}")
        texto_norm = texto_norm.replace(original, novo)

    return texto_norm, hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def extrair_fatos(conn, dt_ini, dt_fim):
    """Fatos agregados no grão ano/mês/empresa/centro/natureza/REF (+ parceiro no RH).

    Retorna (linhas, hash_da_view). dt_fim é exclusivo.
    """
    cur = conn.cursor()
    cur.arraysize = 10000
    view_sql, view_hash = _sql_view_por_periodo(cur)
    sql = f"""
        SELECT EXTRACT(YEAR FROM d.dtcomp)  AS ano,
               EXTRACT(MONTH FROM d.dtcomp) AS mes,
               d.codemp, d.codcencus, d.codnat, d.ref,
               d.codparc,
               SUM(d.valor)     AS valor,
               SUM(d.orcamento) AS orcamento
          FROM ({view_sql}) d
         WHERE d.dtcomp >= :dt_ini AND d.dtcomp < :dt_fim
         GROUP BY EXTRACT(YEAR FROM d.dtcomp), EXTRACT(MONTH FROM d.dtcomp),
                  d.codemp, d.codcencus, d.codnat, d.ref,
                  d.codparc
    """
    cur.execute(sql, dt_ini=dt_ini, dt_fim=dt_fim)
    linhas = cur.fetchall()
    cur.close()
    return linhas, view_hash


def extrair_dimensoes(conn, codparcs):
    """Tabelas de apoio pequenas, sempre recarregadas por inteiro."""
    cur = conn.cursor()
    cur.arraysize = 10000
    dims = {}
    cur.execute("SELECT codcencus, codnat, ref, bloco, titulo, fator FROM vmq_caddre")
    dims["caddre"] = cur.fetchall()
    cur.execute("SELECT codnat, descrnat FROM vmq_tgfnat")
    dims["natureza"] = cur.fetchall()
    cur.execute("SELECT codcencus, descrcencus FROM vmq_tsicus")
    dims["centro"] = cur.fetchall()
    cur.execute("SELECT codemp, razaoabrev FROM vmq_tsiemp")
    dims["empresa"] = [r for r in cur.fetchall() if int(r[0]) not in config.EMPRESAS_EXCLUIDAS]
    parceiros = []
    lista = sorted({int(p) for p in codparcs if p is not None})
    for i in range(0, len(lista), 900):
        lote = lista[i:i + 900]
        binds = ",".join(f":p{j}" for j in range(len(lote)))
        cur.execute(f"SELECT codigo, nome FROM vw_mq_tgfpar_power_bi WHERE codigo IN ({binds})",
                    {f"p{j}": v for j, v in enumerate(lote)})
        parceiros.extend(cur.fetchall())
    dims["parceiro"] = parceiros
    cur.close()
    return dims
