# CTF 知识库 一键启动
#
#   .\start.ps1              启动 Ollama + Web 搜索界面，并打开浏览器
#   .\start.ps1 -Stop        停止全部
#   .\start.ps1 -NoBrowser   不自动开浏览器
#   .\start.ps1 -CpuOnly     强制 CPU 推理（显存被别的程序占了时用）
#   .\start.ps1 -Status      只看状态
#
# 说明：本脚本自己拉起 ollama serve 和 Web 服务，都写到 logs/ 下，
#      进程号记在 logs/*.pid，方便 -Stop 精确关闭。

param(
    [switch]$Stop,
    [switch]$Status,
    [switch]$NoBrowser,
    [switch]$CpuOnly,
    [int]$Port = 8765,
    [int]$OllamaPort = 11434
)

$ErrorActionPreference = 'Stop'
$Root  = $PSScriptRoot
$Venv  = Join-Path $Root '.venv\Scripts\python.exe'
$LogD  = Join-Path $Root 'logs'
$Srv   = Join-Path $Root 'tools\agent\server.py'
$OlExe = Join-Path $Root 'models\ollama-server\ollama.exe'
$OlLib = Join-Path $Root 'models\ollama-server\lib\ollama'
$OlMod = Join-Path $Root 'models\ollama-models'

New-Item -ItemType Directory -Force -Path $LogD | Out-Null

function Say($m, $c = 'Gray') { Write-Host $m -ForegroundColor $c }
function Ok  ($m) { Say "  [OK]   $m" 'Green' }
function Warn($m) { Say "  [警告] $m" 'Yellow' }
function Bad ($m) { Say "  [失败] $m" 'Red' }

# ---------------------------------------------------------------- 工具函数
function Get-PortPid([int]$p) {
    try {
        $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Stop |
             Select-Object -First 1
        if ($c) { return [int]$c.OwningProcess }
    } catch { }
    # 退路：netstat
    $line = netstat -ano | Select-String "LISTENING" |
            Select-String ":$p\s" | Select-Object -First 1
    if ($line -and $line.Line -match '(\d+)\s*$') { return [int]$Matches[1] }
    return 0
}

function Wait-Http([string]$url, [int]$timeout = 40) {
    for ($i = 0; $i -lt ($timeout * 2); $i++) {
        try {
            $r = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing `
                 -ErrorAction Stop
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { return $true }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Stop-ByPidFile([string]$file, [string]$what) {
    if (-not (Test-Path $file)) { return }
    $text = (Get-Content $file -Raw -ErrorAction SilentlyContinue).Trim()
    if ($text -match '^\d+$') {
        $proc = Get-Process -Id ([int]$text) -ErrorAction SilentlyContinue
        if ($proc) {
            try { Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                  Ok "$what 已停止 (pid=$($proc.Id))" }
            catch { Warn "$what 停止失败: $($_.Exception.Message)" }
        }
    }
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------- 状态
function Show-Status {
    $op = Get-PortPid $OllamaPort
    $sp = Get-PortPid $Port
    Say ''
    Say '=== 当前状态 ===' 'Cyan'
    if ($op) { Ok "Ollama   运行中  pid=$op  :$OllamaPort" }
    else     { Warn "Ollama   未运行" }
    if ($sp) { Ok "Web 界面 运行中  pid=$sp  :$Port" }
    else     { Warn "Web 界面 未运行" }

    if ($op) {
        try {
            $tags = Invoke-RestMethod "http://127.0.0.1:$OllamaPort/api/tags" `
                    -TimeoutSec 5
            $ms = $tags.models | ForEach-Object { $_.name }
            Ok ("模型: " + ($ms -join ', '))
        } catch { Warn '模型列表获取失败' }
    }
    Say ''
}

# ---------------------------------------------------------------- 停止
if ($Stop) {
    Say '' ; Say '=== 停止服务 ===' 'Cyan'
    Stop-ByPidFile (Join-Path $LogD 'web.pid') 'Web 界面'
    Stop-ByPidFile (Join-Path $LogD 'ollama.pid') 'Ollama'

    # 兜底：按端口找残留
    foreach ($p in @($Port, $OllamaPort)) {
        $procId = Get-PortPid $p
        if ($procId) {
            try {
                Stop-Process -Id $procId -Force -ErrorAction Stop
                Ok "已关闭占用 :$p 的进程 (pid=$procId)"
            } catch { Warn ":$p 仍被 pid=$procId 占用（可能需要管理员）" }
        }
    }
    Say ''
    Ok '全部停止'
    return
}

if ($Status) { Show-Status; return }

# ---------------------------------------------------------------- 环境检查
Say ''
Say '=== 1. 检查环境 ===' 'Cyan'

if (-not (Test-Path $Venv)) {
    Bad "找不到 venv: $Venv"
    Say '  请先在本目录创建虚拟环境：C:\Python314\python.exe -m venv .venv'
    return
}
Ok 'Python 环境'

if (-not (Test-Path $Srv)) { Bad "找不到 $Srv"; return }
Ok 'Web 服务脚本'

# 前端：优先用 webapp 构建产物，没有就尝试构建，失败则退回单文件界面
$DistDir = Join-Path $Root 'tools\agent\webapp\dist'
$AppDir  = Join-Path $Root 'tools\agent\webapp'
if (Test-Path (Join-Path $DistDir 'index.html')) {
    Ok '前端（已构建）'
} else {
    if (Test-Path (Join-Path $AppDir 'package.json')) {
        Warn '前端未构建，正在构建（首次约 1 分钟）'
        Push-Location $AppDir
        try {
            if (-not (Test-Path (Join-Path $AppDir 'node_modules'))) {
                & npm install --no-audit --no-fund 2>&1 | Out-Null
            }
            & npm run build 2>&1 | Out-Null
        } catch { }
        Pop-Location
        if (Test-Path (Join-Path $DistDir 'index.html')) { Ok '前端构建完成' }
        else { Warn '构建失败，将使用内置简易界面' }
    } else {
        Warn '未找到 webapp，将使用内置简易界面'
    }
}

$hasIndex = Test-Path (Join-Path $Root 'index\fts.db')
if ($hasIndex) { Ok '知识库索引' }
else {
    Warn '索引不存在，正在建立（首次约 4 分钟）'
    Push-Location $Root
    & $Venv (Join-Path $Root 'tools\cli.py') index
    Pop-Location
}

# ---------------------------------------------------------------- Ollama
Say ''
Say '=== 2. Ollama 模型服务 ===' 'Cyan'

$olPid = Get-PortPid $OllamaPort
if ($olPid) {
    Ok "已在运行 (pid=$olPid)"
} else {
    if (-not (Test-Path $OlExe)) {
        Bad "找不到 ollama.exe: $OlExe"
        Say '  模型服务不可用，Web 界面可以检索但无法生成建议。'
    } else {
        $env:OLLAMA_MODELS = $OlMod
        $args = @('serve')
        $sp = Start-Process -FilePath $OlExe -ArgumentList $args `
              -WorkingDirectory $OlLib `
              -RedirectStandardOutput (Join-Path $LogD 'ollama.out.log') `
              -RedirectStandardError  (Join-Path $LogD 'ollama.err.log') `
              -WindowStyle Hidden -PassThru
        $sp.Id | Set-Content (Join-Path $LogD 'ollama.pid') -Encoding ASCII

        if (Wait-Http "http://127.0.0.1:$OllamaPort/api/version" 40) {
            Ok "已启动 (pid=$($sp.Id))"
            try {
                $tags = Invoke-RestMethod "http://127.0.0.1:$OllamaPort/api/tags" `
                        -TimeoutSec 10
                $names = $tags.models | ForEach-Object { $_.name }
                if ($names) { Ok ("模型: " + ($names -join ', ')) }
                else { Warn '还没有导入任何模型，运行 tools\setup_ollama.ps1' }
            } catch { Warn '模型列表获取失败' }
        } else {
            Bad "启动超时，看日志: $(Join-Path $LogD 'ollama.err.log')"
        }
    }
}

# ---------------------------------------------------------------- Web 服务
Say ''
Say '=== 3. Web 搜索界面 ===' 'Cyan'

$webPid = Get-PortPid $Port
if ($webPid) {
    Ok "已在运行 (pid=$webPid)"
} else {
    $env:AGENT_PORT = "$Port"
    $env:AGENT_HOST = '127.0.0.1'
    if (-not $env:AGENT_MODEL) { $env:AGENT_MODEL = 'qwen3-4b-local:latest' }
    if ($CpuOnly) { $env:AGENT_OLLAMA = "http://127.0.0.1:$OllamaPort" }

    Push-Location $Root
    $sp = Start-Process -FilePath $Venv -ArgumentList @($Srv) `
          -WorkingDirectory $Root `
          -RedirectStandardOutput (Join-Path $LogD 'web.out.log') `
          -RedirectStandardError  (Join-Path $LogD 'web.err.log') `
          -WindowStyle Hidden -PassThru
    Pop-Location
    $sp.Id | Set-Content (Join-Path $LogD 'web.pid') -Encoding ASCII

    if (Wait-Http "http://127.0.0.1:$Port/api/health" 30) {
        Ok "已启动 (pid=$($sp.Id))"
    } else {
        Bad "启动超时，看日志: $(Join-Path $LogD 'web.err.log')"
        if (Test-Path (Join-Path $LogD 'web.err.log')) {
            Say '--- 错误日志最后 8 行 ---' 'DarkGray'
            Get-Content (Join-Path $LogD 'web.err.log') -Tail 8 |
                ForEach-Object { Say "  $_" 'DarkGray' }
        }
        return
    }
}

# ---------------------------------------------------------------- 打开
$url = "http://127.0.0.1:$Port/"
Say ''
Say '=== 4. 就绪 ===' 'Cyan'
Ok "界面地址: $url"
Ok "日志目录: $LogD"

if (-not $NoBrowser) {
    try { Start-Process $url; Ok '已打开浏览器' }
    catch { Warn "无法自动打开，请手动访问 $url" }
}

Say ''
Say '提示：' 'DarkGray'
Say '  .\start.ps1 -Status   查看状态' 'DarkGray'
Say '  .\start.ps1 -Stop     停止全部服务' 'DarkGray'
Say ''
