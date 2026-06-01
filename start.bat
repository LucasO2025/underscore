@echo off
title underscore launcher
cd /d "%~dp0"
echo Subindo servidor de waveform (mantenha esta janela aberta enquanto usar o gerador)...
start "underscore server" cmd /k "python server.py"
timeout /t 2 /nobreak >nul
start "" "underscore-gerador.html"
exit
