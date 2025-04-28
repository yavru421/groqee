@echo off
echo ===== STARTING GROQEE 2 =====
echo Opening browser...
start "" "http://127.0.0.1:5000"
echo Waiting for browser to open...
timeout /t 3
echo Starting Groqee application...
start /b "Groqee" "dist\app.exe"
echo Groqee is now running!
echo Access the interface at http://127.0.0.1:5000
pause
