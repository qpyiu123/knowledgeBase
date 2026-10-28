@echo off
REM 在任意位置启用 kb 命令（当前 CMD 会话）
set "KB_ROOT=%~dp0.."
set "PATH=%KB_ROOT%\.venv\Scripts;%PATH%"
set "PYTHONUTF8=1"
doskey kb=python "%KB_ROOT%\tools\cli.py" $*
echo kb 命令已启用（可用: kb search "关键词"）
