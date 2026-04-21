@echo off
cd /d "C:\Users\guilh\Desktop\Alya2"

echo ========================================
echo      ALYA v2.0 COMPLETA
echo ========================================

REM Limpar memoria antiga
del /q "Arcana\armazen\memoria.json" 2>nul

REM Iniciar programa principal
.venv\Scripts\python.exe run.py
pause