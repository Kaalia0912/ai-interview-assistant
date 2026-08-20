@echo off
REM 一键启动（本地 Python 环境）
cd /d %~dp0
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
