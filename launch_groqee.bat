@echo off
echo Starting Groqee 2...
start "" "http://127.0.0.1:5000"
timeout /t 2
start "" "%~dp0\dist\app.exe"
echo Browser and Groqee application launched!
echo If the browser doesn't show Groqee, please navigate to http://127.0.0.1:5000 manually.