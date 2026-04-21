@echo off
cd /d "C:\Users\guilh\Desktop\Alya2"

echo ========================================
echo      ALYA v2.0 - GPU ATIVADO
echo ========================================

REM Limpar memoria antiga
del /q "Arcana\armazen\memoria.json" 2>nul

REM Verificar GPU
python -c "import torch; print('[GPU] CUDA:', torch.cuda.is_available()); print('[GPU] Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')" 2>nul

echo.
echo Iniciando...

REM Usar Python do sistema (tem CUDA)
python run.py
pause