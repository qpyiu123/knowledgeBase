@echo off
setlocal DisableDelayedExpansion
set "ps=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not "%~1"=="" goto with_args
"%ps%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" -NoModel
set "code=%errorlevel%"
if not "%code%"=="0" pause
exit /b %code%

:with_args
"%ps%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
exit /b %errorlevel%
