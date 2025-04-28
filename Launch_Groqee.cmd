@echo off
echo Starting Groqee...
start http://127.0.0.1:5000
timeout /t 2
cd dist
if not exist static mkdir static
if not exist static\groqee_fox mkdir static\groqee_fox
xcopy ..\static\*.* static\ /s /y >nul 2>&1
xcopy ..\evolution_log.py . /y >nul 2>&1
xcopy ..\jdss.json . /y >nul 2>&1
echo Running Groqee...
app.exe
