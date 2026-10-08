"""
Módulo de Governança e Controle de Acessos por Centro de Resultado (CR)
Valida a identidade do gestor e garante restrição estrita nas queries do MariaDB.
"""
import os
import json
import time
import hmac
import hashlib
import pymysql

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIZ_JSON = os.path.join(BASE_DIR, "matriz_acessos.json")

# Chave secreta compartilhada entre Intranet e DRE Gestores
SECRET_KEY = os.getenv("DRE_AUTH_SECRET", "mq-hair-dre-secure-token-2026")

# Administradores com acesso irrestrito a todos os centros
ADMIN_USERS = {"admin", "vagner.luz", "rodrigo.pinhata"}


def normalizar_usuario(usuario):
    if not usuario:
        return ""
    u = str(usuario).strip().lower()
    return u.replace(" ", ".")


def gerar_token_gestor(usuario, expires_in=86400):
    """Gera um token assinado (HMAC-SHA256) com validade de 24h."""
    usuario_norm = normalizar_usuario(usuario)
    exp = int(time.time()) + expires_in
    payload = f"{usuario_norm}:{exp}"
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def validar_token_gestor(token):
    """Valida a assinatura e expiração do token recebido da Intranet."""
    if not token or ":" not in token:
        return None
    parts = token.split(":")
    if len(parts) != 3:
        return None
    usuario_norm, exp_str, sig = parts
    try:
        exp = int(exp_str)
    except ValueError:
        return None

    if time.time() > exp:
        return None  # Token expirado

    expected_payload = f"{usuario_norm}:{exp}"
    expected_sig = hmac.new(SECRET_KEY.encode(), expected_payload.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(sig, expected_sig):
        return usuario_norm
    return None


def obter_permissoes_gestor(usuario, db_conn=None):
    """
    Retorna os centros de resultado autorizados para o gestor.
    Se for admin, is_admin = True e centros = None (irrestrito).
    """
    usuario_norm = normalizar_usuario(usuario)
    if not usuario_norm:
        # Se nenhum usuário informado em ambiente de desenvolvimento, trata como anônimo / restrito
        return {"usuario": "", "is_admin": False, "centros": [], "canal": "", "detalhes": []}

    if usuario_norm in ADMIN_USERS:
        return {"usuario": usuario_norm, "is_admin": True, "centros": None, "canal": "Diretoria", "detalhes": []}

    # Tenta consultar MariaDB primeiro
    centros = []
    detalhes = []
    canal = ""

    conn = db_conn
    close_conn = False
    try:
        if conn is None:
            conn = pymysql.connect(
                host=os.getenv("MARIADB_HOST", "192.168.1.22"),
                user=os.getenv("MARIADB_USER", "antonio"),
                password=os.getenv("MARIADB_PASSWORD", "yzmpq100"),
                database=os.getenv("MARIADB_DB", "dre_gestores"),
                port=int(os.getenv("MARIADB_PORT", "3306"))
            )
            close_conn = True

        with conn.cursor() as cur:
            cur.execute("""
                SELECT codcencus, centro_resultado, canal
                  FROM Acessos_Usuario_CR
                 WHERE usuario = %s AND ativo = 1
                 ORDER BY codcencus
            """, (usuario_norm,))
            rows = cur.fetchall()
            for cod, desc, cnl in rows:
                centros.append(int(cod))
                detalhes.append({"codigo": int(cod), "descricao": desc, "canal": cnl})
                if not canal and cnl:
                    canal = cnl

    except Exception as e:
        print(f"[WARN] Erro ao consultar Acessos_Usuario_CR no banco: {e}. Usando fallback JSON.")
    finally:
        if close_conn and conn:
            try:
                conn.close()
            except Exception:
                pass

    # Fallback no arquivo JSON caso banco esteja inacessível
    if not centros and os.path.exists(MATRIZ_JSON):
        try:
            with open(MATRIZ_JSON, "r", encoding="utf-8") as f:
                matriz = json.load(f)
            for r in matriz:
                if normalizar_usuario(r.get("usuario")) == usuario_norm:
                    cod = int(r["codcencus"])
                    centros.append(cod)
                    detalhes.append({"codigo": cod, "descricao": r["centro_resultado"], "canal": r["canal"]})
                    if not canal:
                        canal = r["canal"]
        except Exception:
            pass

    return {
        "usuario": usuario_norm,
        "is_admin": False,
        "centros": centros,
        "canal": canal,
        "detalhes": detalhes
    }


def verificar_acesso_centro(permissoes, codcencus):
    """Retorna True se o gestor tem acesso ao centro informado."""
    if permissoes.get("is_admin"):
        return True
    if str(codcencus).upper() == "ALL":
        return True
    try:
        cod_int = int(codcencus)
        return cod_int in permissoes.get("centros", [])
    except (ValueError, TypeError):
        return False
