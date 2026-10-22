@echo off
cd /d "%~dp0"
set "HF_ENDPOINT=https://hf-mirror.com"
set "PYW=%~dp0.venv\Scripts\pythonw.exe"
if not exist "%PYW%" (
  powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('找不到运行环境 .venv','翻译飘窗')"
  exit /b 1
)
start "" "%PYW%" -s "%~dp0main.py"
