@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 翻译飘窗(调试)
set "HF_ENDPOINT=https://hf-mirror.com"
"%~dp0.venv\Scripts\python.exe" -s "%~dp0main.py"
echo.
echo 已退出，退出码 %ERRORLEVEL%
pause
