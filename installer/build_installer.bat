@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set ISCC="%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
  echo Inno Setup 6 not found. Install from https://jrsoftware.org/isdl.php
  pause
  exit /b 1
)
if not exist vendor\MicrosoftEdgeWebview2Setup.exe (
  echo Missing vendor\MicrosoftEdgeWebview2Setup.exe
  echo See vendor\README.txt for download links.
  pause
  exit /b 1
)
if not exist vendor\VC_redist.x64.exe (
  echo Missing vendor\VC_redist.x64.exe
  echo See vendor\README.txt for download links.
  pause
  exit /b 1
)
%ISCC% ImpedanceMatchingAI.iss
