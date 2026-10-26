@echo off
chcp 65001 >nul
cd /d "%~dp0"
python app\run_mcp.py
