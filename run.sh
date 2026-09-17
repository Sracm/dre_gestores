#!/bin/bash
# Servidor DRE Gestores - Geral (Porta 5100)

cd "$(dirname "$0")"
echo "========================================================"
echo "  Iniciando DRE Gestores - Geral (Porta 5100)"
echo "========================================================"
echo "Local:   http://localhost:5100/"
echo ""
python3 app.py
