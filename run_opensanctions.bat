@echo off
set SCRIPT_DIR=C:\Users\HP\Desktop\Desktop Stuff\pythondel
set LOGFILE=%SCRIPT_DIR%\log.txt

echo ----------------------------- >> "%LOGFILE%"
echo Running OpenSanctions at %date% %time% >> "%LOGFILE%"
"C:\Users\HP\AppData\Local\Microsoft\WindowsApps\python.exe" "%SCRIPT_DIR%\new.py" >> "%LOGFILE%" 2>&1
echo Finished at %date% %time% >> "%LOGFILE%"
