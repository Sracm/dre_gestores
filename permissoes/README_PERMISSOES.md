# 🔐 Governança de Acessos por Centro de Resultado (DRE Gestores)

Esta pasta gerencia as permissões dos gestores da MQ HAIR para visualização exclusiva de seus centros de custo.

## Arquivos:
- `Acessos_Usuario_CR.sql`: DDL da tabela oficial no MariaDB.
- `matriz_acessos.json`: Matriz estruturada de Gestor x Centros x Canais.
- `matriz_acessos.csv`: Planilha legível para conferência e auditoria.
- `controle_acesso.py`: Módulo Python que valida tokens e aplica cláusulas WHERE nas queries.
- `seed_acessos.py`: Script de carga e atualização da tabela no MariaDB.
