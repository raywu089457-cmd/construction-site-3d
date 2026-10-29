@echo off
rem static server + export API for the asset demos, restart loop so the phone URL never dies
cd /d C:\Users\ray\assets\web
:loop
"C:\Users\ray\voice-loop\.venv\Scripts\python.exe" "C:\Users\ray\assets\web\serve.py" --port 4211 --root C:/Users/ray/assets/web >> "_srv.out" 2>> "_srv.err"
timeout /t 3 /nobreak >nul
goto loop
