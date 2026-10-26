@echo off
chcp 65001 >nul
title 智配芯生 · ImpedanceMCP
cd /d "%~dp0"
python app\run_app.py
if errorlevel 1 pause
