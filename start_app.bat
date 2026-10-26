@echo off
chcp 65001 >nul
title Impedance Matching AI
cd /d "%~dp0"
python app\run_app.py
if errorlevel 1 pause
