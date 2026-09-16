@echo off
title Servidor DRE Gestores - Geral (Porta 5100)
cd /d "%~dp0"
echo ========================================================
echo   Iniciando DRE Gestores - Geral (Porta 5100)
echo ========================================================
echo Local:   http://localhost:5100/
echo Rede:    http://10.11.1.162:5100/
echo.
python app.py
pause
