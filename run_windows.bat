@echo off
REM Double-click this file on Windows to start the assistant.
REM First time only, run these once in Command Prompt:
REM   pip install requests
REM   ollama pull llama3.2:3b
cd /d "%~dp0"
python main.py
pause
