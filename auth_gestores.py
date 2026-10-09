"""
auth_gestores.py - Modulo de Governanca e Autenticacao de Gestores
Ponto de entrada oficial para app.py do DRE Gestores.
"""
from permissoes.controle_acesso import (
    obter_permissoes_gestor,
    validar_token_gestor,
    verificar_acesso_centro,
    ADMIN_USERS,
    gerar_token_gestor,
    normalizar_usuario
)

__all__ = [
    "obter_permissoes_gestor",
    "validar_token_gestor",
    "verificar_acesso_centro",
    "ADMIN_USERS",
    "gerar_token_gestor",
    "normalizar_usuario"
]
