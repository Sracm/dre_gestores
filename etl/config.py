"""Configuração do ETL, lida de variáveis de ambiente / arquivo .env na raiz do projeto."""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

ORACLE_USER = os.getenv("ORACLE_USER", "sankhya")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_DSN = os.getenv("ORACLE_DSN", "192.168.1.55/ORCL")

# Banco SQLite consumido pelo app.py (recomendado: fora do OneDrive)
DB_PATH = os.getenv("DRE_DB_PATH", os.path.join(BASE_DIR, "dre_cache.db"))
LOG_DIR = os.getenv("DRE_LOG_DIR", os.path.join(BASE_DIR, "logs"))

# Quantidade de meses atualizados na carga incremental, contando o mês atual
# (2 = mês anterior + mês atual). Meses mais antigos não são tocados.
MESES_ATUALIZAR = int(os.getenv("DRE_MESES_ATUALIZAR", "2"))
# Início da base (mesmo corte usado na VMQ_DREQLIK)
DATA_INICIO_BASE = os.getenv("DRE_DATA_INICIO", "2024-01-01")

# ── Regras de negócio espelhadas do modelo Power BI ────────────────────────
BLOCOS_DRE = (
    "1.Venda Liquida",
    "3.Despesas com Vendas",
    "4.Despesas Comercial Operacional",
    "5.Despesas Administrativa Operacional",
    "6.Receitas/Despesas Financeiras",
)
EMPRESAS_EXCLUIDAS = (7, 8, 9, 10, 502)          # filtro do Power Query em VMQ_TSIEMP
NATUREZAS_BONIF = (12010301, 12010302)            # chave bonif2 / fator2
TITULO_BONIF = "2.Bonificação Clientes"
TITULO_IMPOSTOS_BONIF = "3.Impostos s/ bonificações"
BLOCO_DESP_VENDAS = "3.Despesas com Vendas"
CENTROS_DETALHE_PARCEIRO = (9010000,)             # guia DRE DETALHE (RH)

# Queda máxima aceita no realizado absoluto de um mês já passado, em relação
# ao que está publicado, antes de abortar a carga (proteção contra extração parcial).
VALIDACAO_TOLERANCIA = float(os.getenv("DRE_VALIDACAO_TOLERANCIA", "0.20"))
