# 备份全部知识库、索引、工作区、反馈和上传附件；保留已有备份。
# 恢复：.\backup.ps1 -Restore backup\ctf_kb_xxx.zip -Destination work\restore-check
param([string]$Restore, [string]$Destination, [string]$PythonExe = '')
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'tools\python-runtime.ps1')
$python = (Resolve-KbPython -Root $PSScriptRoot -PythonExe $PythonExe).Path
$arguments = @((Join-Path $PSScriptRoot 'tools\backup_data.py'), '--root', $PSScriptRoot)
if ($Restore) {
    if (-not $Destination) { throw '请用 -Destination 指定一个新的空目录' }
    $arguments += @('--restore', $Restore, '--destination', $Destination)
}
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw '备份或恢复失败，请查看上面的具体原因' }
