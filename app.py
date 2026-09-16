import os
import sys
import sqlite3
import traceback
import threading
import time
import subprocess
import datetime as dt
from collections import OrderedDict
from flask import Flask, render_template, jsonify, request, redirect, url_for
from typing import List

from dotenv import load_dotenv

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
DB_PATH = os.getenv("DRE_DB_PATH", os.path.join(BASE_DIR, "dre_cache.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

# ── Versão dos dados (gravada pelo ETL em etl_status) ───────────────────────
_versao = {"info": None, "ts": 0.0}
_versao_lock = threading.Lock()
VERSAO_TTL = 5  # segundos

def versao_dados():
    """Última carga publicada pelo ETL; consultada no máximo a cada VERSAO_TTL."""
    with _versao_lock:
        if _versao["info"] is not None and time.time() - _versao["ts"] < VERSAO_TTL:
            return _versao["info"]
    info = {"versao": 0, "atualizado_em": None, "status": None, "erro": None}
    try:
        with get_db() as conn:
            ok = conn.execute(
                "SELECT id, fim FROM etl_status WHERE status = 'sucesso' ORDER BY id DESC LIMIT 1"
            ).fetchone()
            ultima = conn.execute(
                "SELECT status, erro, inicio FROM etl_status WHERE status <> 'executando' ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if ok:
            info["versao"], info["atualizado_em"] = ok["id"], ok["fim"]
        if ultima:
            info["status"], info["erro"] = ultima["status"], ultima["erro"]
    except sqlite3.OperationalError:
        pass  # etl_status ainda não existe (banco gerado pelo processo antigo)
    with _versao_lock:
        _versao["info"], _versao["ts"] = info, time.time()
    return info

# ── In-Memory Cache (ultra-rápido) ──────────────────────────────────────────
# As chaves levam a versão dos dados: uma nova carga do ETL invalida tudo.
_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 600  # 10 minutos

def cache_get(key):
    key = f"v{versao_dados()['versao']}:{key}"
    with _cache_lock:
        entry = _cache.get(key)
        if entry and (time.time() - entry["ts"]) < CACHE_TTL:
            return entry["data"]
    return None

def cache_set(key, data):
    prefixo = f"v{versao_dados()['versao']}:"
    with _cache_lock:
        for antiga in [k for k in _cache if not k.startswith(prefixo)]:
            del _cache[antiga]
        _cache[prefixo + key] = {"data": data, "ts": time.time()}

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO SIMPLES DE REGIONAIS / GESTORES
# ═══════════════════════════════════════════════════════════════════════════
# Cada regional mapeia para os seus respectivos centros de custo
REGIONAIS = {
    "regional.fsp": {
        "slug": "regional.fsp",
        "nome": "Regional FSP",
        "gestor": "Ricardo Pavão",
        "centros": [
            1020000,  # DISTRIBUICAO
            1010200,  # VAREJO - RJ
            1010300,  # VAREJO - ND
            1010400   # VAREJO - SUL
        ]
    },
    "rh": {
        "slug": "rh",
        "nome": "RH",
        "gestor": "Recursos Humanos",
        "centros": [
            9010000   # RH
        ]
    },
    "produto": {
        "slug": "produto",
        "nome": "Desenvolvimento de Produtos",
        "gestor": "Desenvolvimento",
        "centros": [
            10020000
        ]
    },
    "logistica": {
        "slug": "logistica",
        "nome": "Logística",
        "gestor": "Operações / Logística",
        "centros": [
            4010500,
            4010600,
            4010700,
            4010800
        ]
    },
    "comex": {
        "slug": "comex",
        "nome": "Comex",
        "gestor": "Comércio Exterior",
        "centros": [
            1050000,
            23000000,
            23010000,
            23020000,
            24000000,
            24010101
        ]
    },
    "assistencia": {
        "slug": "assistencia",
        "nome": "Assistência Técnica & SAC",
        "gestor": "Assistência Técnica e SAC",
        "centros": [
            3000000,
            3010000,
            2010000
        ]
    },
    "regional-sp": {
        "slug": "regional-sp",
        "nome": "Regional SP",
        "gestor": "Varejo",
        "centros": [
            1010100
        ]
    }
}
# Aliases amigáveis
REGIONAIS["regional-fsp"] = REGIONAIS["regional.fsp"]
REGIONAIS["fsp"] = REGIONAIS["regional.fsp"]
REGIONAIS["recursos-humanos"] = REGIONAIS["rh"]
REGIONAIS["recursoshumanos"] = REGIONAIS["rh"]
REGIONAIS["produtos"] = REGIONAIS["produto"]
REGIONAIS["logística"] = REGIONAIS["logistica"]
REGIONAIS["comercio-exterior"] = REGIONAIS["comex"]
REGIONAIS["comercioexterior"] = REGIONAIS["comex"]
REGIONAIS["assistencia-tecnica"] = REGIONAIS["assistencia"]
REGIONAIS["assistenciatecnica"] = REGIONAIS["assistencia"]
REGIONAIS["sac"] = REGIONAIS["assistencia"]
REGIONAIS["varejo-sp"] = REGIONAIS["regional-sp"]

# ═══════════════════════════════════════════════════════════════════════════
#  ROTAS DE PÁGINAS (DIRETORIA & LINKS DEDICADOS POR REGIONAL)
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    """Visão Geral / Diretoria (acesso total com seletor de regionais)"""
    return render_template("index.html", regional=None)

@app.route("/<slug>")
def regional_view(slug):
    """Link dedicado para a Regional (ex: /regional.fsp ou /fsp)"""
    clean_slug = slug.lower().strip()
    if clean_slug in REGIONAIS:
        return render_template("index.html", regional=REGIONAIS[clean_slug])
    return redirect(url_for("index"))

ALLOWED_COMPANIES = [
    'Consolidação', 'FORX', 'MCR - FABRICA', 'MCR - FILIAL 03', 
    'MCR - MATRIZ', 'MCR - SC', 'QUALITY - RJ', 'QUALITY MATRIZ', 
    'SL ONLINE - SP', 'VLS - RJ', 'VLS - SP', 'FORX MG'
]
EXCLUDED_CODCENCUS = 21010000

def parse_cenc_param(cenc_raw):
    if not cenc_raw or cenc_raw == "ALL":
        return []
    items = []
    for part in str(cenc_raw).split(","):
        part = part.strip()
        if part and part != "ALL":
            try:
                items.append(int(part))
            except ValueError:
                pass
    return items

def parse_int_list(raw, default=None):
    if not raw or raw == "ALL":
        return default if default is not None else []
    items = []
    for part in str(raw).split(","):
        part = part.strip()
        if part and part != "ALL":
            try:
                items.append(int(part))
            except ValueError:
                pass
    return items if items else (default if default is not None else [])

def parse_str_list(raw):
    if not raw or raw == "ALL":
        return []
    items = []
    for part in str(raw).split(","):
        part = part.strip()
        if part and part != "ALL":
            items.append(part)
    return items

def resolve_effective_cenc(regional_slug, cenc_raw):
    """
    Se for informada uma Regional, restringe os centros de custo estritamente aos dela.
    Caso contrário, respeita o filtro global ou cenc_raw.
    """
    clean_slug = str(regional_slug).lower().strip() if regional_slug else ""
    regional_info = REGIONAIS.get(clean_slug)

    if regional_info:
        allowed = set(regional_info["centros"])
        requested = parse_cenc_param(cenc_raw)
        if not requested:
            return sorted(list(allowed))
        inter = [c for c in requested if c in allowed]
        return sorted(inter) if inter else sorted(list(allowed))
    
    return parse_cenc_param(cenc_raw)

# ═══════════════════════════════════════════════════════════════════════════
#  FILTROS
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/api/filtros")
def filtros():
    regional_raw = request.args.get("regional", "").strip().lower()
    regional_info = REGIONAIS.get(regional_raw)
    cache_key = f"filtros_{regional_info['slug']}" if regional_info else "filtros_geral"

    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            # Anos disponíveis
            cur.execute("""
                SELECT DISTINCT ano FROM dre_filtros_anos 
                WHERE ano >= 2023 AND ano <= 2027 
                ORDER BY ano DESC
            """)
            anos = [int(r["ano"]) for r in cur.fetchall()]
            if not anos:
                anos = [2026, 2025, 2024, 2023]

            # Empresas disponíveis
            placeholders = ",".join(["?"] * len(ALLOWED_COMPANIES))
            cur.execute(f"""
                SELECT nome FROM dre_filtros_empresas 
                WHERE nome IN ({placeholders})
                ORDER BY nome
            """, ALLOWED_COMPANIES)
            empresas = [{"CODEMP": r["nome"], "NOME": r["nome"]} for r in cur.fetchall()]

            # Centros de Custo
            if regional_info:
                allowed_cencs = regional_info["centros"]
                ph = ",".join(["?"] * len(allowed_cencs))
                cur.execute(f"""
                    SELECT codcencus, nome FROM dre_filtros_centros 
                    WHERE codcencus IN ({ph}) AND codcencus != {EXCLUDED_CODCENCUS}
                    ORDER BY codcencus
                """, allowed_cencs)
                centros = [
                    {"CODCENCUS": r["codcencus"], "NOME": f"{r['codcencus']} - {r['nome']}"}
                    for r in cur.fetchall()
                ]
            else:
                cur.execute(f"""
                    SELECT codcencus, nome FROM dre_filtros_centros 
                    WHERE codcencus > 0 AND codcencus != {EXCLUDED_CODCENCUS}
                    ORDER BY codcencus
                """)
                centros = [
                    {"CODCENCUS": r["codcencus"], "NOME": f"{r['codcencus']} - {r['nome']}"}
                    for r in cur.fetchall()
                ]

        meses = [
            {"NUM": i + 1, "NOME": n}
            for i, n in enumerate([
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ])
        ]

        # Lista de regionais configuradas
        regionais_lista = [
            {"slug": "regional.fsp", "nome": "Regional FSP (Ricardo Pavão)"},
            {"slug": "rh", "nome": "RH (Recursos Humanos)"}
        ]

        result = {
            "anos": anos,
            "meses": meses,
            "empresas": empresas,
            "centros": centros,
            "regionais": regionais_lista,
            "regional_ativa": regional_info["slug"] if regional_info else None
        }
        cache_set(cache_key, result)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500

# ═══════════════════════════════════════════════════════════════════════════
#  VERSÃO DOS DADOS (consultada pelo front para auto-atualizar)
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/api/versao")
def api_versao():
    resp = jsonify(versao_dados())
    resp.headers["Cache-Control"] = "no-store"
    return resp

# ═══════════════════════════════════════════════════════════════════════════
#  STATUS DO JOB
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/api/dre/status")
def dre_status():
    key = request.args.get("key", "")
    cached = cache_get(key)
    if cached:
        return jsonify({"status": "done", **cached})
    return jsonify({"status": "done"})

# ═══════════════════════════════════════════════════════════════════════════
#  DRE — DADOS PRINCIPAIS
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/api/dre")
def dre():
    try:
        ano_raw = request.args.get("ano", "2026")
        mes_raw = request.args.get("mes", "8")
        emp_raw = request.args.get("emp", "ALL")
        cenc_raw = request.args.get("cenc", "ALL")
        regional_raw = request.args.get("regional", None)

        cenc_list = resolve_effective_cenc(regional_raw, cenc_raw)
        cenc_str = ",".join(str(c) for c in cenc_list) if cenc_list else "ALL"

        key = f"dre_{ano_raw}_{mes_raw}_{emp_raw}_{cenc_str}"
        cached = cache_get(key)
        if cached:
            return jsonify(cached)

        anos = parse_int_list(ano_raw, [2026])
        meses = parse_int_list(mes_raw, [8])
        emps = parse_str_list(emp_raw)

        ano_primario = max(anos) if anos else 2026
        mes_primario = max(meses) if meses else 8

        ano_mom, mes_mom = (ano_primario, mes_primario - 1) if mes_primario > 1 else (ano_primario - 1, 12)
        ano_yoy = ano_primario - 1

        # Meses YTD (de janeiro até o maior mês selecionado)
        meses_ytd = list(range(1, mes_primario + 1))
        meses_ant = list(set(meses_ytd + ([12] if mes_primario == 1 else [])))

        ph_anos = ",".join(["?"] * len(anos))
        ph_meses = ",".join(["?"] * len(meses))
        ph_ytd = ",".join(["?"] * len(meses_ytd))
        ph_ant = ",".join(["?"] * len(meses_ant))

        is_rh = False
        is_fsp = False
        is_produto = False
        is_logistica = False
        is_comex = False
        is_assistencia = False
        is_sp = False
        if regional_raw:
            clean_slug = str(regional_raw).lower().strip()
            if clean_slug in ("rh", "recursos-humanos", "recursoshumanos"):
                is_rh = True
            elif clean_slug in ("regional.fsp", "fsp"):
                is_fsp = True
            elif clean_slug in ("produto", "produtos"):
                is_produto = True
            elif clean_slug in ("logistica", "logística"):
                is_logistica = True
            elif clean_slug in ("comex", "comercio-exterior", "comercioexterior"):
                is_comex = True
            elif clean_slug in ("assistencia", "assistencia-tecnica", "assistenciatecnica", "sac"):
                is_assistencia = True
            elif clean_slug in ("regional-sp", "varejo-sp"):
                is_sp = True

        is_special = is_rh or is_fsp or is_produto or is_logistica or is_comex or is_assistencia or is_sp
        tabela = "dre_detalhe_rh" if is_rh else "dre_detalhe_fsp" if is_special else "dre_data"

        where = [
            f"((ano IN ({ph_anos}) AND mes IN ({ph_ytd})) OR (ano = ? AND mes IN ({ph_ant})))"
        ]
        params = [
            *anos, *meses_ytd,
            ano_yoy, *meses_ant
        ]

        if not is_special:
            where.append("codcencus != ?")
            params.append(EXCLUDED_CODCENCUS)
            
            if emps:
                ph_emp = ",".join(["?"] * len(emps))
                where.append(f"empresa IN ({ph_emp})")
                params.extend(emps)
            else:
                placeholders = ",".join(["?"] * len(ALLOWED_COMPANIES))
                where.append(f"empresa IN ({placeholders})")
                params.extend(ALLOWED_COMPANIES)

        if cenc_list:
            if len(cenc_list) == 1:
                where.append("codcencus = ?")
                params.append(cenc_list[0])
            else:
                ph_cenc = ",".join(["?"] * len(cenc_list))
                where.append(f"codcencus IN ({ph_cenc})")
                params.extend(cenc_list)

        where_sql = " AND ".join(where)

        sql = f"""
            SELECT
                bloco,
                titulo,
                descrnat,
                SUM(CASE WHEN ano IN ({ph_anos}) AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) AS realizado,
                SUM(CASE WHEN ano IN ({ph_anos}) AND mes IN ({ph_meses}) THEN orcado ELSE 0 END) AS orcado,
                SUM(CASE WHEN ano = ? AND mes = ? THEN realizado ELSE 0 END) AS real_mom,
                SUM(CASE WHEN ano = ? AND mes = ? THEN orcado ELSE 0 END) AS orc_mom,
                SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) AS real_yoy,
                SUM(CASE WHEN ano IN ({ph_anos}) AND mes IN ({ph_ytd}) THEN realizado ELSE 0 END) AS real_ytd,
                SUM(CASE WHEN ano = ? AND mes IN ({ph_ytd}) THEN realizado ELSE 0 END) AS real_ytd_ant
            FROM {tabela}
            WHERE {where_sql}
            GROUP BY bloco, titulo, descrnat
            HAVING (
                SUM(CASE WHEN ano IN ({ph_anos}) AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) != 0 OR
                SUM(CASE WHEN ano IN ({ph_anos}) AND mes IN ({ph_meses}) THEN orcado ELSE 0 END) != 0
            )
            ORDER BY bloco, titulo, descrnat
        """
        query_params = [
            *anos, *meses,
            *anos, *meses,
            ano_mom, mes_mom,
            ano_mom, mes_mom,
            ano_yoy, *meses,
            *anos, *meses_ytd,
            ano_yoy, *meses_ytd,
            *params,
            *anos, *meses,
            *anos, *meses
        ]

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(sql, query_params)
            rows = [dict(r) for r in cur.fetchall()]

        bonif_total = sum(
            float(r.get("realizado") or 0)
            for r in rows
            if r.get("titulo") and "bonif" in str(r["titulo"]).lower()
        )

        dre_tree = _build_dre_tree(rows, bonif_total)
        result = {"dre": dre_tree, "bonif_total": bonif_total}
        cache_set(key, result)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500

# ═══════════════════════════════════════════════════════════════════════════
#  DRE MENSAL (Evolução dos 12 meses para gráfico)
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/api/dre/mensal")
def dre_mensal():
    try:
        ano_raw = request.args.get("ano", "2026")
        emp_raw = request.args.get("emp", "ALL")
        cenc_raw = request.args.get("cenc", "ALL")
        regional_raw = request.args.get("regional", None)
        bloco = request.args.get("bloco", None)
        titulo = request.args.get("titulo", None)
        descrnat = request.args.get("descrnat", None)

        is_rh = False
        is_fsp = False
        is_produto = False
        is_logistica = False
        is_comex = False
        is_assistencia = False
        is_sp = False
        if regional_raw:
            clean_slug = str(regional_raw).lower().strip()
            if clean_slug in ("rh", "recursos-humanos", "recursoshumanos"):
                is_rh = True
            elif clean_slug in ("regional.fsp", "fsp"):
                is_fsp = True
            elif clean_slug in ("produto", "produtos"):
                is_produto = True
            elif clean_slug in ("logistica", "logística"):
                is_logistica = True
            elif clean_slug in ("comex", "comercio-exterior", "comercioexterior"):
                is_comex = True
            elif clean_slug in ("assistencia", "assistencia-tecnica", "assistenciatecnica", "sac"):
                is_assistencia = True
            elif clean_slug in ("regional-sp", "varejo-sp"):
                is_sp = True

        is_special = is_rh or is_fsp or is_produto or is_logistica or is_comex or is_assistencia or is_sp

        cenc_list = resolve_effective_cenc(regional_raw, cenc_raw)
        cenc_str = ",".join(str(c) for c in cenc_list) if cenc_list else "ALL"

        key = f"mensal_{ano_raw}_{emp_raw}_{cenc_str}_{bloco}_{titulo}_{descrnat}"
        cached = cache_get(key)
        if cached:
            return jsonify(cached)

        anos = parse_int_list(ano_raw, [2026])
        emps = parse_str_list(emp_raw)

        ph_anos = ",".join(["?"] * len(anos))
        where = [f"ano IN ({ph_anos})"]
        params = [*anos]

        if not is_special:
            where.append("codcencus != ?")
            params.append(EXCLUDED_CODCENCUS)

            if emps:
                ph_emp = ",".join(["?"] * len(emps))
                where.append(f"empresa IN ({ph_emp})")
                params.extend(emps)
            else:
                placeholders = ",".join(["?"] * len(ALLOWED_COMPANIES))
                where.append(f"empresa IN ({placeholders})")
                params.extend(ALLOWED_COMPANIES)

        if cenc_list:
            if len(cenc_list) == 1:
                where.append("codcencus = ?")
                params.append(cenc_list[0])
            else:
                ph_cenc = ",".join(["?"] * len(cenc_list))
                where.append(f"codcencus IN ({ph_cenc})")
                params.extend(cenc_list)

        use_dre_data = False

        if descrnat:
            where.append("descrnat = ?")
            params.append(descrnat)
            use_dre_data = True
            if titulo:
                where.append("titulo = ?")
                params.append(titulo)
            if bloco:
                where.append("bloco = ?")
                params.append(bloco)
        elif titulo:
            where.append("titulo = ?")
            params.append(titulo)
            use_dre_data = True
            if bloco:
                where.append("bloco = ?")
                params.append(bloco)
        elif bloco and bloco.upper() != "MARGEM DE CONTRIBUIÇÃO":
            where.append("bloco = ?")
            params.append(bloco)

        where_sql = " AND ".join(where)
        table_name = "dre_data" if use_dre_data else "dre_resumo_mensal"
        if is_special:
            table_name = "dre_detalhe_rh" if is_rh else "dre_detalhe_fsp"

        sql = f"""
            SELECT
                mes AS MES,
                bloco AS BLOCO,
                SUM(realizado) AS REALIZADO,
                SUM(orcado) AS ORCADO
            FROM {table_name}
            WHERE {where_sql}
            GROUP BY mes, bloco
            ORDER BY mes, bloco
        """

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = [dict(r) for r in cur.fetchall()]

        result = {"mensal": rows}
        cache_set(key, result)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500

# ═══════════════════════════════════════════════════════════════════════════
#  DRE POR EMPRESA (Gráfico por Empresa)
# ═══════════════════════════════════════════════════════════════════════════
@app.route("/api/dre/por-empresa")
def dre_por_empresa():
    try:
        ano_raw = request.args.get("ano", "2026")
        mes_raw = request.args.get("mes", "8")
        emp_raw = request.args.get("emp", "ALL")
        cenc_raw = request.args.get("cenc", "ALL")
        regional_raw = request.args.get("regional", None)

        cenc_list = resolve_effective_cenc(regional_raw, cenc_raw)
        cenc_str = ",".join(str(c) for c in cenc_list) if cenc_list else "ALL"

        key = f"empresa_{ano_raw}_{mes_raw}_{emp_raw}_{cenc_str}"
        cached = cache_get(key)
        if cached:
            return jsonify(cached)

        anos = parse_int_list(ano_raw, [2026])
        meses = parse_int_list(mes_raw, [8])
        emps = parse_str_list(emp_raw)

        ph_anos = ",".join(["?"] * len(anos))
        ph_meses = ",".join(["?"] * len(meses))
        where = [f"ano IN ({ph_anos})", f"mes IN ({ph_meses})", "empresa IS NOT NULL", "empresa != ''", "codcencus != ?"]
        params = [*anos, *meses, EXCLUDED_CODCENCUS]

        if emps:
            ph_emp = ",".join(["?"] * len(emps))
            where.append(f"empresa IN ({ph_emp})")
            params.extend(emps)
        else:
            placeholders = ",".join(["?"] * len(ALLOWED_COMPANIES))
            where.append(f"empresa IN ({placeholders})")
            params.extend(ALLOWED_COMPANIES)

        if cenc_list:
            if len(cenc_list) == 1:
                where.append("codcencus = ?")
                params.append(cenc_list[0])
            else:
                ph_cenc = ",".join(["?"] * len(cenc_list))
                where.append(f"codcencus IN ({ph_cenc})")
                params.extend(cenc_list)

        where_sql = " AND ".join(where)

        sql = f"""
            SELECT
                empresa AS EMPRESA,
                bloco AS BLOCO,
                SUM(realizado) AS REALIZADO,
                SUM(orcado) AS ORCADO
            FROM dre_resumo_mensal
            WHERE {where_sql}
            GROUP BY empresa, bloco
            ORDER BY empresa, bloco
        """

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = [dict(r) for r in cur.fetchall()]

        result = {"por_empresa": rows}
        cache_set(key, result)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500

# ═══════════════════════════════════════════════════════════════════════════
#  HELPER: Constrói Árvore Hierárquica do DRE
# ═══════════════════════════════════════════════════════════════════════════
def _build_dre_tree(detalhe, bonif_total):
    blocos_dict = OrderedDict()

    for r in detalhe:
        bloco    = r.get("bloco")  or r.get("BLOCO")  or ""
        titulo   = r.get("titulo") or r.get("TITULO") or ""
        descr    = r.get("descrnat") or r.get("DESCRNAT") or ""
        real     = float(r.get("realizado") or r.get("REALIZADO") or 0)
        orc      = float(r.get("orcado") or r.get("ORCADO") or 0)
        real_mom = float(r.get("real_mom") or 0)
        orc_mom  = float(r.get("orc_mom") or 0)
        real_yoy = float(r.get("real_yoy") or 0)
        real_ytd = float(r.get("real_ytd") or 0)
        real_ytd_ant = float(r.get("real_ytd_ant") or 0)

        # Ignora linhas vazias (0 realizado e 0 orçado no mês atual)
        if abs(real) < 0.001 and abs(orc) < 0.001:
            continue

        if bloco not in blocos_dict:
            blocos_dict[bloco] = {
                "bloco": bloco,
                "realizado": 0.0,
                "orcado": 0.0,
                "real_mom": 0.0,
                "orc_mom": 0.0,
                "real_yoy": 0.0,
                "real_ytd": 0.0,
                "real_ytd_ant": 0.0,
                "titulos": OrderedDict()
            }

        if titulo not in blocos_dict[bloco]["titulos"]:
            blocos_dict[bloco]["titulos"][titulo] = {
                "titulo": titulo,
                "realizado": 0.0,
                "orcado": 0.0,
                "real_mom": 0.0,
                "orc_mom": 0.0,
                "real_yoy": 0.0,
                "real_ytd": 0.0,
                "real_ytd_ant": 0.0,
                "linhas": []
            }

        blocos_dict[bloco]["titulos"][titulo]["linhas"].append({
            "descr": descr,
            "realizado": real,
            "orcado": orc,
            "real_mom": real_mom,
            "orc_mom": orc_mom,
            "real_yoy": real_yoy,
            "real_ytd": real_ytd,
            "real_ytd_ant": real_ytd_ant,
        })
        blocos_dict[bloco]["titulos"][titulo]["realizado"] += real
        blocos_dict[bloco]["titulos"][titulo]["orcado"]    += orc
        blocos_dict[bloco]["titulos"][titulo]["real_mom"]  += real_mom
        blocos_dict[bloco]["titulos"][titulo]["orc_mom"]   += orc_mom
        blocos_dict[bloco]["titulos"][titulo]["real_yoy"]  += real_yoy
        blocos_dict[bloco]["titulos"][titulo]["real_ytd"]  += real_ytd
        blocos_dict[bloco]["titulos"][titulo]["real_ytd_ant"] += real_ytd_ant
        blocos_dict[bloco]["realizado"] += real
        blocos_dict[bloco]["orcado"]    += orc
        blocos_dict[bloco]["real_mom"]  += real_mom
        blocos_dict[bloco]["orc_mom"]   += orc_mom
        blocos_dict[bloco]["real_yoy"]  += real_yoy
        blocos_dict[bloco]["real_ytd"]  += real_ytd
        blocos_dict[bloco]["real_ytd_ant"] += real_ytd_ant

    # Base para cálculo de % sobre Venda Bruta (conforme DAX [VENDA BRUTA ORCADO] / [VENDA BRUTA REALIZADO])
    vb_real = 0.0
    vb_orc = 0.0
    for b, bd in blocos_dict.items():
        for t, td in bd["titulos"].items():
            if "venda bruta" in t.lower():
                vb_real = td["realizado"]
                vb_orc = td["orcado"]
                break
        if vb_real:
            break

    if not vb_real:
        vb_real = 1.0
    if not vb_orc:
        vb_orc = 1.0

    margem_real    = sum(bd["realizado"] for bd in blocos_dict.values())
    margem_orc     = sum(bd["orcado"]    for bd in blocos_dict.values())
    margem_real_mom = sum(bd["real_mom"]  for bd in blocos_dict.values())
    margem_orc_mom  = sum(bd["orc_mom"]   for bd in blocos_dict.values())
    margem_yoy     = sum(bd["real_yoy"]  for bd in blocos_dict.values())
    margem_real_ytd = sum(bd["real_ytd"]  for bd in blocos_dict.values())
    margem_real_ytd_ant = sum(bd["real_ytd_ant"] for bd in blocos_dict.values())

    def pct(n, d):
        return round((n / d) * 100, 1) if d else None

    # DAX formula oficial: DIVIDE(Realizado - Orçado, ABS(Orçado), 0)
    def ro(r, o):
        if not o or abs(o) < 0.001:
            return None
        return round(((r - o) / abs(o)) * 100, 1)

    # Variação MoM, YoY e YTD YoY: (Realizado - Base) / ABS(Base) * 100
    def calc_var(r, b):
        if b is None or abs(b) < 0.001:
            return None
        return round(((r - b) / abs(b)) * 100, 1)

    result = []
    
    # 1. Margem de Contribuição no TOPO, exatamente como no Power BI Matrix
    if len(blocos_dict) > 0:
        result.append({
            "bloco": "MARGEM DE CONTRIBUIÇÃO",
            "is_total": True,
            "realizado": margem_real,
            "orcado": margem_orc,
            "real_mom": margem_real_mom,
            "orc_mom": margem_orc_mom,
            "mom": calc_var(margem_real, margem_real_mom),
            "yoy": calc_var(margem_real, margem_yoy),
            "ytd_yoy": calc_var(margem_real_ytd, margem_real_ytd_ant),
            "pct_real": pct(margem_real, vb_real),
            "pct_orc": pct(margem_orc, vb_orc),
            "ro": ro(margem_real, margem_orc),
            "titulos": [],
        })

    # 2. Blocos, Títulos e Detalhes
    for bloco, bd in blocos_dict.items():
        titulos_out = []
        for titulo, td in bd["titulos"].items():
            linhas_out = [
                {
                    "descr": ln["descr"],
                    "realizado": ln["realizado"],
                    "orcado": ln["orcado"],
                    "mom": calc_var(ln["realizado"], ln["real_mom"]),
                    "yoy": calc_var(ln["realizado"], ln["real_yoy"]),
                    "ytd_yoy": calc_var(ln["real_ytd"], ln["real_ytd_ant"]),
                    "pct_real": pct(ln["realizado"], vb_real),
                    "pct_orc": pct(ln["orcado"], vb_orc),
                    "ro": ro(ln["realizado"], ln["orcado"]),
                }
                for ln in td["linhas"]
            ]
            titulos_out.append({
                "titulo": titulo,
                "realizado": td["realizado"],
                "orcado": td["orcado"],
                "real_mom": td["real_mom"],
                "orc_mom": td["orc_mom"],
                "mom": calc_var(td["realizado"], td["real_mom"]),
                "yoy": calc_var(td["realizado"], td["real_yoy"]),
                "ytd_yoy": calc_var(td["real_ytd"], td["real_ytd_ant"]),
                "pct_real": pct(td["realizado"], vb_real),
                "pct_orc": pct(td["orcado"], vb_orc),
                "ro": ro(td["realizado"], td["orcado"]),
                "linhas": linhas_out,
            })

        result.append({
            "bloco": bloco,
            "realizado": bd["realizado"],
            "orcado": bd["orcado"],
            "real_mom": bd["real_mom"],
            "orc_mom": bd["orc_mom"],
            "mom": calc_var(bd["realizado"], bd["real_mom"]),
            "yoy": calc_var(bd["realizado"], bd["real_yoy"]),
            "ytd_yoy": calc_var(bd["real_ytd"], bd["real_ytd_ant"]),
            "pct_real": pct(bd["realizado"], vb_real),
            "pct_orc": pct(bd["orcado"], vb_orc),
            "ro": ro(bd["realizado"], bd["orcado"]),
            "titulos": titulos_out,
        })

    return result

@app.route("/api/dre/detalhe")
def api_dre_detalhe():
    """
    Endpoint para a guia DRE DETALHE.
    Retorna árvore hierárquica com o mesmo formato do DRE Gestores:
      Margem de Contribuição -> Bloco -> Título -> Natureza -> Parceiro
    com orcado, realizado, mom, yoy, ytd_yoy, ro em todos os níveis.
    """
    ano = request.args.get("ano", 2026, type=int)
    trimestre = request.args.get("trimestre", None)
    busca = request.args.get("q", "").strip().lower()
    mes_raw = request.args.get("mes", None)

    conn = get_db()
    cur = conn.cursor()

    # 1. Anos disponíveis
    cur.execute("SELECT DISTINCT ano FROM dre_detalhe_rh ORDER BY ano")
    anos_disp = [r[0] for r in cur.fetchall()]
    if not anos_disp:
        anos_disp = [2023, 2024, 2025, 2026]

    # 2. Meses selecionados
    month_names = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
        5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
        9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    short_names = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    if not mes_raw or mes_raw == "ALL":
        meses_ativos = list(range(1, 13))
    else:
        meses_ativos = []
        for p in str(mes_raw).split(","):
            p = p.strip()
            if p and p.isdigit():
                m = int(p)
                if 1 <= m <= 12:
                    meses_ativos.append(m)
        if not meses_ativos:
            meses_ativos = [9]

    mes_primario = max(meses_ativos)
    ano_mom, mes_mom = (ano, mes_primario - 1) if mes_primario > 1 else (ano - 1, 12)
    ano_yoy = ano - 1
    meses_ytd = list(range(1, mes_primario + 1))

    # 3. Gráficos Trimestral e Mensal
    cur.execute("""
        SELECT tri_ano, SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
        GROUP BY tri_ano
        ORDER BY tri_ano
    """, (ano,))
    quarterly = []
    for r in cur.fetchall():
        tri_label = r["tri_ano"] or ""
        tri_clean = tri_label.split("-")[0] if "-" in tri_label else tri_label
        quarterly.append({
            "trimestre": tri_clean or tri_label,
            "tri_ano": tri_label,
            "orcado": round(float(r["orcado"] or 0), 2),
            "realizado": round(float(r["realizado"] or 0), 2)
        })

    cur.execute("""
        SELECT mes, nomemes, SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
        GROUP BY mes, nomemes
        ORDER BY mes
    """, (ano,))
    monthly_map = {r["mes"]: r for r in cur.fetchall()}
    monthly = []
    for m in range(1, 13):
        if m in monthly_map:
            mr = monthly_map[m]
            monthly.append({
                "mes": m,
                "nomemes": short_names.get(m, mr["nomemes"]),
                "orcado": round(float(mr["orcado"] or 0), 2),
                "realizado": round(float(mr["realizado"] or 0), 2)
            })
        else:
            monthly.append({
                "mes": m,
                "nomemes": short_names.get(m, f"M{m}"),
                "orcado": 0.0,
                "realizado": 0.0
            })

    regional_raw = request.args.get("regional", None)
    emp_raw = request.args.get("emp", "ALL")
    cenc_raw = request.args.get("cenc", "ALL")
    cenc_list = resolve_effective_cenc(regional_raw, cenc_raw)

    is_rh = False
    is_fsp = False
    is_produto = False
    is_logistica = False
    is_comex = False
    is_assistencia = False
    is_sp = False
    if regional_raw:
        clean_slug = str(regional_raw).lower().strip()
        if clean_slug in ("rh", "recursos-humanos", "recursoshumanos"):
            is_rh = True
        elif clean_slug in ("regional.fsp", "fsp"):
            is_fsp = True
        elif clean_slug in ("produto", "produtos"):
            is_produto = True
        elif clean_slug in ("logistica", "logística"):
            is_logistica = True
        elif clean_slug in ("comex", "comercio-exterior", "comercioexterior"):
            is_comex = True
        elif clean_slug in ("assistencia", "assistencia-tecnica", "assistenciatecnica", "sac"):
            is_assistencia = True
        elif clean_slug in ("regional-sp", "varejo-sp"):
            is_sp = True

    is_special = is_rh or is_fsp or is_produto or is_logistica or is_comex or is_assistencia or is_sp

    ph_meses = ",".join("?" for _ in meses_ativos)
    ph_ytd = ",".join("?" for _ in meses_ytd)

    where_busca = ""
    extra_params = []
    if busca:
        where_busca = " AND (LOWER(bloco) LIKE ? OR LOWER(titulo) LIKE ? OR LOWER(descrnat) LIKE ? "
        if is_special:
            where_busca += "OR LOWER(parceiro) LIKE ?)"
            extra_params = [f"%{busca}%"] * 4
        else:
            where_busca += ")"
            extra_params = [f"%{busca}%"] * 3

    if is_special:
        tabela = "dre_detalhe_rh" if is_rh else "dre_detalhe_fsp"
        
        if tabela == "dre_detalhe_fsp" and cenc_list:
            ph_cenc = ",".join(["?"] * len(cenc_list))
            where_busca += f" AND codcencus IN ({ph_cenc})"
            extra_params.extend(cenc_list)
            
        sql = f"""
            SELECT bloco, titulo, descrnat, parceiro,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN orcado ELSE 0 END) as orcado,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) as realizado,
                   SUM(CASE WHEN ano = ? AND mes = ? THEN realizado ELSE 0 END) as real_mom,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) as real_yoy,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_ytd}) THEN realizado ELSE 0 END) as real_ytd,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_ytd}) THEN realizado ELSE 0 END) as real_ytd_ant
            FROM {tabela}
            WHERE ((ano IN (?, ?) AND mes IN ({ph_ytd})) OR (ano = ? AND mes = ?)){where_busca}
            GROUP BY bloco, titulo, descrnat, parceiro
            ORDER BY bloco, titulo, descrnat, parceiro
        """
        params = [
            ano, *meses_ativos,
            ano, *meses_ativos,
            ano_mom, mes_mom,
            ano_yoy, *meses_ativos,
            ano, *meses_ytd,
            ano_yoy, *meses_ytd,
            ano, ano_yoy, *meses_ytd,
            ano_mom, mes_mom,
            *extra_params
        ]
    else:
        # dre_data query
        where = [f"((ano IN (?, ?) AND mes IN ({ph_ytd})) OR (ano = ? AND mes = ?))"]
        params = [ano, ano_yoy, *meses_ytd, ano_mom, mes_mom]
        
        where.append("codcencus != ?")
        params.append(EXCLUDED_CODCENCUS)
        
        emps = parse_str_list(emp_raw)
        if emps:
            ph_emp = ",".join(["?"] * len(emps))
            where.append(f"empresa IN ({ph_emp})")
            params.extend(emps)
        else:
            placeholders = ",".join(["?"] * len(ALLOWED_COMPANIES))
            where.append(f"empresa IN ({placeholders})")
            params.extend(ALLOWED_COMPANIES)
            
        if cenc_list:
            if len(cenc_list) == 1:
                where.append("codcencus = ?")
                params.append(cenc_list[0])
            else:
                ph_cenc = ",".join(["?"] * len(cenc_list))
                where.append(f"codcencus IN ({ph_cenc})")
                params.extend(cenc_list)
        
        if where_busca:
            where.append(where_busca.strip(" AND"))
            params.extend(extra_params)
            
        where_sql = " AND ".join(where)

        sql = f"""
            SELECT bloco, titulo, descrnat, '<SEM PARCEIRO>' as parceiro,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN orcado ELSE 0 END) as orcado,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) as realizado,
                   SUM(CASE WHEN ano = ? AND mes = ? THEN realizado ELSE 0 END) as real_mom,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_meses}) THEN realizado ELSE 0 END) as real_yoy,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_ytd}) THEN realizado ELSE 0 END) as real_ytd,
                   SUM(CASE WHEN ano = ? AND mes IN ({ph_ytd}) THEN realizado ELSE 0 END) as real_ytd_ant
            FROM dre_data
            WHERE {where_sql}
            GROUP BY bloco, titulo, descrnat
            ORDER BY bloco, titulo, descrnat
        """
        full_params = [
            ano, *meses_ativos,
            ano, *meses_ativos,
            ano_mom, mes_mom,
            ano_yoy, *meses_ativos,
            ano, *meses_ytd,
            ano_yoy, *meses_ytd,
            *params
        ]
        params = full_params

    cur.execute(sql, params)
    raw_rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    def calc_var(r, b):
        if b is None or abs(b) < 0.001: return None
        return round(((r - b) / abs(b)) * 100, 1)

    def calc_ro(r, o):
        if not o or abs(o) < 0.001: return None
        return round(((r - o) / abs(o)) * 100, 1)

    blocos = OrderedDict()
    for r in raw_rows:
        b = (r["bloco"] or "Outros").strip()
        t = (r["titulo"] or "Outros").strip()
        n = (r["descrnat"] or "Sem Natureza").strip()
        p = (r["parceiro"] or "<SEM PARCEIRO>").strip()

        orc = float(r["orcado"] or 0)
        real = float(r["realizado"] or 0)
        rmom = float(r["real_mom"] or 0)
        ryoy = float(r["real_yoy"] or 0)
        rytd = float(r["real_ytd"] or 0)
        rytd_ant = float(r["real_ytd_ant"] or 0)

        if b not in blocos:
            blocos[b] = {"orc": 0.0, "real": 0.0, "rmom": 0.0, "ryoy": 0.0, "rytd": 0.0, "rytd_ant": 0.0, "titulos": OrderedDict()}
        if t not in blocos[b]["titulos"]:
            blocos[b]["titulos"][t] = {"orc": 0.0, "real": 0.0, "rmom": 0.0, "ryoy": 0.0, "rytd": 0.0, "rytd_ant": 0.0, "linhas": OrderedDict()}
        if n not in blocos[b]["titulos"][t]["linhas"]:
            blocos[b]["titulos"][t]["linhas"][n] = {"orc": 0.0, "real": 0.0, "rmom": 0.0, "ryoy": 0.0, "rytd": 0.0, "rytd_ant": 0.0, "parceiros": []}

        blocos[b]["orc"] += orc
        blocos[b]["real"] += real
        blocos[b]["rmom"] += rmom
        blocos[b]["ryoy"] += ryoy
        blocos[b]["rytd"] += rytd
        blocos[b]["rytd_ant"] += rytd_ant

        blocos[b]["titulos"][t]["orc"] += orc
        blocos[b]["titulos"][t]["real"] += real
        blocos[b]["titulos"][t]["rmom"] += rmom
        blocos[b]["titulos"][t]["ryoy"] += ryoy
        blocos[b]["titulos"][t]["rytd"] += rytd
        blocos[b]["titulos"][t]["rytd_ant"] += rytd_ant

        blocos[b]["titulos"][t]["linhas"][n]["orc"] += orc
        blocos[b]["titulos"][t]["linhas"][n]["real"] += real
        blocos[b]["titulos"][t]["linhas"][n]["rmom"] += rmom
        blocos[b]["titulos"][t]["linhas"][n]["ryoy"] += ryoy
        blocos[b]["titulos"][t]["linhas"][n]["rytd"] += rytd
        blocos[b]["titulos"][t]["linhas"][n]["rytd_ant"] += rytd_ant

        if abs(real) > 0.001 or (p != "<SEM PARCEIRO>" and abs(orc) > 0.001):
            blocos[b]["titulos"][t]["linhas"][n]["parceiros"].append({
                "parceiro": p,
                "orcado": round(orc, 2),
                "realizado": round(real, 2),
                "mom": calc_var(real, rmom),
                "yoy": calc_var(real, ryoy),
                "ytd_yoy": calc_var(rytd, rytd_ant),
                "ro": calc_ro(real, orc)
            })

    dre_tree = []
    tot_orc = sum(bd["orc"] for bd in blocos.values())
    tot_real = sum(bd["real"] for bd in blocos.values())
    tot_rmom = sum(bd["rmom"] for bd in blocos.values())
    tot_ryoy = sum(bd["ryoy"] for bd in blocos.values())
    tot_rytd = sum(bd["rytd"] for bd in blocos.values())
    tot_rytd_ant = sum(bd["rytd_ant"] for bd in blocos.values())

    # Margem de Contribuição no topo
    dre_tree.append({
        "bloco": "MARGEM DE CONTRIBUIÇÃO",
        "is_total": True,
        "orcado": round(tot_orc, 2),
        "realizado": round(tot_real, 2),
        "mom": calc_var(tot_real, tot_rmom),
        "yoy": calc_var(tot_real, tot_ryoy),
        "ytd_yoy": calc_var(tot_rytd, tot_rytd_ant),
        "ro": calc_ro(tot_real, tot_orc),
        "titulos": []
    })

    for b, bd in blocos.items():
        if abs(bd["orc"]) < 0.01 and abs(bd["real"]) < 0.01:
            continue
        titulos_list = []
        for t, td in bd["titulos"].items():
            if abs(td["orc"]) < 0.01 and abs(td["real"]) < 0.01:
                continue
            linhas_list = []
            for n, nd in td["linhas"].items():
                if abs(nd["orc"]) < 0.01 and abs(nd["real"]) < 0.01:
                    continue
                nd["parceiros"].sort(key=lambda x: abs(x["realizado"]), reverse=True)
                linhas_list.append({
                    "descr": n,
                    "orcado": round(nd["orc"], 2),
                    "realizado": round(nd["real"], 2),
                    "mom": calc_var(nd["real"], nd["rmom"]),
                    "yoy": calc_var(nd["real"], nd["ryoy"]),
                    "ytd_yoy": calc_var(nd["rytd"], nd["rytd_ant"]),
                    "ro": calc_ro(nd["real"], nd["orc"]),
                    "parceiros": nd["parceiros"]
                })
            titulos_list.append({
                "titulo": t,
                "orcado": round(td["orc"], 2),
                "realizado": round(td["real"], 2),
                "mom": calc_var(td["real"], td["rmom"]),
                "yoy": calc_var(td["real"], td["ryoy"]),
                "ytd_yoy": calc_var(td["rytd"], td["rytd_ant"]),
                "ro": calc_ro(td["real"], td["orc"]),
                "linhas": linhas_list
            })
        dre_tree.append({
            "bloco": b,
            "orcado": round(bd["orc"], 2),
            "realizado": round(bd["real"], 2),
            "mom": calc_var(bd["real"], bd["rmom"]),
            "yoy": calc_var(bd["real"], bd["ryoy"]),
            "ytd_yoy": calc_var(bd["rytd"], bd["rytd_ant"]),
            "ro": calc_ro(bd["real"], bd["orc"]),
            "titulos": titulos_list
        })

    return jsonify({
        "status": "success",
        "ano": ano,
        "anos_disponiveis": anos_disp,
        "quarterly": quarterly,
        "monthly": monthly,
        "dre": dre_tree
    })

@app.route("/api/dre/update", methods=["POST"])
def dre_update():
    try:
        # Executa o ETL de forma síncrona
        result = subprocess.run([sys.executable, "-m", "etl.atualizar_dados"], cwd=BASE_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": result.stderr})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, port=5100, host="0.0.0.0", threaded=True)

