# 在当前 PowerShell 会话里启用 kb 命令（点号调用：. .\tools\activate.ps1）
$script:KB_ROOT = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
. (Join-Path $PSScriptRoot 'python-runtime.ps1')
$script:KB_PYTHON_EXE = (Resolve-KbPython -Root $script:KB_ROOT).Path
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function kb {
    & $script:KB_PYTHON_EXE "$script:KB_ROOT\tools\cli.py" @args
}

function kb-search { kb search @args }

Write-Host "kb 命令已启用。示例：" -ForegroundColor Green
Write-Host '  kb search "n相同 e不同 两组密文"'
Write-Host '  kb ask "附件是 pyc，有花指令"'
Write-Host '  kb doctor'
