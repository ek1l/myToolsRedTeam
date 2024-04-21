@echo off

python --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
  echo Python não está instalado. Por favor, instale Python para continuar.
  exit /b 1
)
 
pip --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
  echo pip não está instalado. Por favor, instale pip para continuar.
  exit /b 1
)

pip install -r requirements.txt

echo Instalação concluída!
