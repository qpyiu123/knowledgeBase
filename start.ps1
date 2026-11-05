# CTF 知识库 一键启动
#
#   .\start.ps1              启动 Qwen3.5 + Web 搜索界面，并打开浏览器
#   .\start.ps1 -Start       同上（显式启动开关）
#   .\start.ps1 -Stop        停止全部服务
#   .\start.ps1 -Status      只看状态（[Web] / [索引] / [模型] 三层独立显示）
#   .\start.ps1 -Reindex     重建索引（FTS + 向量，前台显示进度）
#   .\start.ps1 -NoBrowser   不自动开浏览器
#   .\start.ps1 -CpuOnly     强制 CPU 推理（显存被别的程序占了时用）
#   .\start.ps1 -NoModel     只启动查询界面
#   .\start.ps1 -ChatModel qwen35-4b  使用可选的 4B 模型（默认 9B）
#   .\start.ps1 -PythonExe <路径>  临时选择 Python（也可使用 KB_PYTHON / config.toml）
#   .\start.ps1 -CheckEnvironment  检查实际 Python 与依赖，不启动服务
#
# 说明：本脚本拉起配置中选择的模型服务和 Web，日志写到 logs/ 下。
#      pid 文件记录的是按端口反查到的“真实监听进程”，不是 Start-Process 外壳；
#      -Stop 先按监听端口关闭，再核对 pid 文件，避免关错或留下孤儿监听。

param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Reindex,
    [switch]$NoBrowser,
    [switch]$CpuOnly,
    [switch]$NoModel,
    [switch]$CheckEnvironment,
    [string]$PythonExe = '',
    [string]$LogDirectory = '',
    [ValidateSet('', 'qwen35-9b', 'qwen35-4b')]
    [string]$ChatModel = '',
    [int]$Port = 8765,
    [int]$OllamaPort = 11434
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$Root  = $PSScriptRoot
. (Join-Path $Root 'tools\python-runtime.ps1')
$RuntimeChoice = $null
$Venv = ''
if (-not $Stop) {
    try {
        $RuntimeChoice = Resolve-KbPython -Root $Root -PythonExe $PythonExe
        $Venv = $RuntimeChoice.Path
    } catch {
        if ($Status) { Write-Warning $_.Exception.Message }
        else { throw }
    }
}
$LogD  = Join-Path $Root 'logs'
if ($LogDirectory) {
    $LogD = if ([IO.Path]::IsPathRooted($LogDirectory)) { $LogDirectory } else { Join-Path $Root $LogDirectory }
}
$Srv   = Join-Path $Root 'tools\agent\server.py'
$OlExe = Join-Path $Root 'models\ollama-server\ollama.exe'
$OlLib = Join-Path $Root 'models\ollama-server\lib\ollama'
$OlMod = Join-Path $Root 'models\ollama-models'
$BuildScript = Join-Path $Root 'tools\agent\buildinfo.py'
$CliScript   = Join-Path $Root 'tools\cli.py'
$LlamaScript = Join-Path $Root 'tools\llama_runtime.py'
$PreviousChatModel = $env:KB_CHAT_MODEL
try {
$Backend = 'llama_server'
if ($ChatModel) { $env:KB_CHAT_MODEL = $ChatModel }

New-Item -ItemType Directory -Force -Path $LogD | Out-Null

function Say($m, $c = 'Gray') { Write-Host $m -ForegroundColor $c }
function Ok  ($m) { Say "  [OK]   $m" 'Green' }
function Warn($m) { Say "  [警告] $m" 'Yellow' }
function Bad ($m) { Say "  [失败] $m" 'Red' }

if ($CheckEnvironment) {
    $report = Test-KbPython -Root $Root -PythonExe $Venv
    $report | Add-Member -NotePropertyName selected_by -NotePropertyValue $RuntimeChoice.Source
    $report | ConvertTo-Json -Depth 6
    return
}
if ($Venv) {
    $LlamaConfig = (& $Venv -X utf8 $LlamaScript command | ConvertFrom-Json)
    $Backend = $LlamaConfig.backend
}

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

function Get-ProcCommandLine([int]$procId) {
    if (-not $procId) { return '' }
    try {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId = $procId" `
             -ErrorAction Stop
        if ($p -and $p.CommandLine) { return [string]$p.CommandLine }
    } catch { }
    try {
        $p = Get-WmiObject Win32_Process -Filter "ProcessId = $procId" `
             -ErrorAction Stop
        if ($p -and $p.CommandLine) { return [string]$p.CommandLine }
    } catch { }
    return ''
}

function Test-ProjectProcess([int]$procId) {
    $cmd = Get-ProcCommandLine $procId
    if (-not $cmd) { return $false }
    return ($cmd.IndexOf($Root, [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
}

function Get-Health([int]$p, [int]$timeout = 5) {
    try {
        return Invoke-RestMethod "http://127.0.0.1:$p/api/health" `
               -TimeoutSec $timeout -ErrorAction Stop
    } catch { return $null }
}

function Get-ExpectedBuild {
    if (-not (Test-Path $Venv) -or -not (Test-Path $BuildScript)) { return '' }
    try {
        $out = & $Venv $BuildScript 2>$null
        if ($LASTEXITCODE -ne 0) { return '' }
        $line = @($out) | Where-Object { "$_".Trim() } | Select-Object -Last 1
        if ($line) { return "$line".Trim() }
    } catch { }
    return ''
}

function Get-ExpectedConfig {
    if (-not (Test-Path $Venv) -or -not (Test-Path $BuildScript)) { return '' }
    try {
        $out = & $Venv $BuildScript --config 2>$null
        if ($LASTEXITCODE -ne 0) { return '' }
        $line = @($out) | Where-Object { "$_".Trim() } | Select-Object -Last 1
        if ($line) { return "$line".Trim() }
    } catch { }
    return ''
}

function Get-ConfiguredModel {
    $cfg = Join-Path $Root 'config.toml'
    if (-not (Test-Path $cfg)) { return '' }
    try {
        $inOllama = $false
        foreach ($line in Get-Content -LiteralPath $cfg -Encoding UTF8) {
            if ($line -match '^\s*\[([^\]]+)\]\s*$') {
                $inOllama = ($Matches[1].Trim() -eq 'ollama')
                continue
            }
            if ($inOllama -and $line -match '^\s*model\s*=\s*(.+?)\s*$') {
                $value = $Matches[1].Trim().Trim('"').Trim("'")
                if ($value) { return $value }
            }
        }
    } catch { }
    return ''
}

function Show-LogTail([string]$name, [int]$lines = 15) {
    $candidates = @(
        (Join-Path $LogD "$name.log"),
        (Join-Path $LogD "$name.err.log"),
        (Join-Path $LogD "$name.out.log")
    )
    $shown = $false
    foreach ($file in $candidates) {
        if (-not (Test-Path -LiteralPath $file)) { continue }
        Say "--- $file 最后 $lines 行 ---" 'DarkGray'
        try {
            Get-Content -LiteralPath $file -Tail $lines -ErrorAction Stop |
                ForEach-Object { Say "  $_" 'DarkGray' }
        } catch {
            Say "  （读取失败: $($_.Exception.Message)）" 'DarkGray'
        }
        $shown = $true
    }
    if (-not $shown) {
        Say "  （日志不存在：$($candidates -join '、')）" 'DarkGray'
    }
}

function Show-StartupAdvice([int]$p) {
    $tip = ("  建议：确认 :{0} 未被其他程序占用（可用 -Port / -OllamaPort 换端口）；" +
            "查看上面日志的完整内容；若进程被拦截请检查杀毒软件/防火墙。") -f $p
    Say $tip 'Yellow'
}

function Show-ModelStatus {
    if ($Backend -in @('none', 'off')) { Ok '模型解释已关闭'; return }
    if ($Backend -eq 'llama_server') {
        if ($Venv) { & $Venv -X utf8 $LlamaScript status }
        else { Warn '请指定可用 Python 后检查模型状态' }
        return
    }
    try {
        $op = Get-PortPid $OllamaPort
        if (-not $op) {
            Warn "Ollama 未启动，Web 检索仍可用但“问模型”不可用（:$OllamaPort 未监听）"
            return
        }
        try {
            $tags = Invoke-RestMethod "http://127.0.0.1:$OllamaPort/api/tags" `
                    -TimeoutSec 5 -ErrorAction Stop
        } catch {
            Warn "Ollama 端口 :$OllamaPort 已监听 (pid=$op)，但 /api/tags 不可达"
            return
        }
        $names = @($tags.models | ForEach-Object { $_.name })
        if ($names.Count -gt 0) {
            Ok ("Ollama 运行中 (pid={0})，模型: {1}" -f $op, ($names -join ', '))
            return
        }
        $expected = Get-ConfiguredModel
        if ($expected) {
            Warn "Ollama 已启动 (pid=$op)，但没有可用模型；缺少模型: $expected（运行 tools\setup_ollama.ps1 导入）"
        } else {
            Warn "Ollama 已启动 (pid=$op)，但没有可用模型（运行 tools\setup_ollama.ps1 导入）"
        }
    } catch {
        Warn "模型状态检查失败: $($_.Exception.Message)"
    }
}

function Show-WebStatus {
    try {
        $sp = Get-PortPid $Port
        if (-not $sp) {
            Warn "Web 未运行（:$Port 未监听）"
            return
        }
        Ok "Web 运行中  pid=$sp  :$Port"
        try {
            $h = Get-Health $Port
            if (-not $h) {
                Warn "端口 :$Port 已监听，但 /api/health 不可用，无法确认后端版本"
                return
            }
            if ($h.runtime) {
                Ok ("运行环境: Python {0} / {1}" -f $h.runtime.version, $h.runtime.executable)
                if ($Venv -and $h.runtime.executable -and $h.runtime.executable -ne $Venv) {
                    Warn ("本次选择 {0}；当前服务仍使用原环境，请重启本项目服务后切换" -f $Venv)
                }
            }
            $running = ''
            if ($null -ne $h.build) { $running = "$($h.build)".Trim() }
            $expected = Get-ExpectedBuild
            if (-not $running) {
                Warn '检测到旧版本后端正在运行（health 无 build 字段），建议先 .\start.ps1 -Stop 再 -Start'
            } elseif ($expected -and $running -ne $expected) {
                Warn "检测到旧版本后端正在运行（运行中 build=$running，当前代码=$expected），建议先 .\start.ps1 -Stop 再 -Start"
            } else {
                Ok "后端版本一致 (build=$running)"
            }
            $runningCfg = ''
            if ($null -ne $h.config) { $runningCfg = "$($h.config)".Trim() }
            $expectedCfg = Get-ExpectedConfig
            if (-not $runningCfg) {
                Warn '后端 health 无 config 字段（旧版本），无法判断配置/前端产物是否变化'
            } elseif ($expectedCfg -and $runningCfg -ne $expectedCfg) {
                Warn "配置或前端产物已变（运行中 config=$runningCfg，当前=$expectedCfg），建议重启后端"
            }
        } catch {
            Warn "后端版本检查失败: $($_.Exception.Message)"
        }
    } catch {
        Warn "Web 状态检查失败: $($_.Exception.Message)"
    }
}

function Show-IndexStatus {
    try {
        Show-IndexFreshness
    } catch {
        Warn "索引状态检查失败: $($_.Exception.Message)"
    }
}

function Get-IndexInfo {
    $db = Join-Path $Root 'index\fts.db'
    if (-not (Test-Path $db)) { return $null }
    $kbDir = Join-Path $Root 'kb'
    # 篇数以 index\manifest.json 为准（与 tools\kb\manifest.py 同一套收录规则）；
    # 清单不存在时才退回本地扫描，兼容旧索引。
    $manifestPath = Join-Path $Root 'index\manifest.json'
    $manifestCount = $null
    if (Test-Path $manifestPath) {
        try {
            $m = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($m -and ($m.version -eq 1) -and ($null -ne $m.files)) {
                $manifestCount = @($m.files.PSObject.Properties).Count
            }
        } catch {
            $manifestCount = $null
        }
    }
    $files = @()
    if (Test-Path $kbDir) {
        # 与 tools\kb\parser.py:iter_docs 保持一致：跳过 _templates/.obsidian/.git/
        # node_modules 目录，以及文件名以 _ 开头的 Markdown（如 kb/_index.md）。
        $skipDirRe = '(^|[\\/])(_templates|\.obsidian|\.git|node_modules)[\\/]'
        $kbFull = [string](Get-Item -LiteralPath $kbDir).FullName
        $files = @(Get-ChildItem -LiteralPath $kbDir -Recurse -Filter *.md `
                   -File -ErrorAction SilentlyContinue | Where-Object {
            if ($_.Name.StartsWith('_')) { return $false }
            $rel = $_.FullName.Substring($kbFull.Length).TrimStart('\')
            return -not ($rel -match $skipDirRe)
        })
    }
    $latest = $files | Sort-Object LastWriteTime -Descending |
              Select-Object -First 1
    $dbTime = (Get-Item -LiteralPath $db).LastWriteTime
    $latestTime = $null
    $latestPath = ''
    if ($latest) {
        $latestTime = $latest.LastWriteTime
        $latestPath = $latest.FullName
    }
    $mtimeStale = $false
    if ($latestTime -and $latestTime -gt $dbTime) { $mtimeStale = $true }
    $mdCount = $files.Count
    $fromManifest = $false
    if ($null -ne $manifestCount) {
        $mdCount = [int]$manifestCount
        $fromManifest = $true
    }
    return [pscustomobject]@{
        DbTime       = $dbTime
        MdCount      = $mdCount
        FromManifest = $fromManifest
        LatestTime   = $latestTime
        LatestPath   = $latestPath
        MtimeStale   = $mtimeStale
    }
}

function Get-FtsStats {
    if (-not (Test-Path $Venv)) { return $null }
    $tools = Join-Path $Root 'tools'
    # 注意：Windows PowerShell 5.1 传原生参数会吞掉双引号，Python 代码里只用单引号。
    $code = "import json,sys; sys.path.insert(0, r'$tools'); " +
            "from kb.config import Config; from kb.fts import FtsIndex; " +
            "c=Config.load(); " +
            "print(json.dumps(FtsIndex(c.index_dir / 'fts.db').stats(), ensure_ascii=False))"
    try {
        $out = & $Venv -c $code 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) {
            return (($out -join "`n") | ConvertFrom-Json)
        }
    } catch { }
    return $null
}

function Show-IndexFreshness {
    $info = Get-IndexInfo
    if (-not $info) {
        Warn '索引不存在，运行 .\start.ps1 -Reindex 建立'
        return
    }
    $docs = -1
    $h = Get-Health $Port
    if ($h -and $h.index -and ($null -ne $h.index.docs)) {
        $docs = [int]$h.index.docs
    } else {
        $st = Get-FtsStats
        if ($st -and ($null -ne $st.docs)) { $docs = [int]$st.docs }
    }
    $issues = @()
    if ($info.MtimeStale) {
        $issues += ("kb 最新更新 {0:yyyy-MM-dd HH:mm} 晚于索引 {1:yyyy-MM-dd HH:mm}" -f $info.LatestTime, $info.DbTime)
    }
    if ($docs -ge 0 -and $docs -ne $info.MdCount) {
        $issues += ("kb {0} 篇，索引 {1} 篇" -f $info.MdCount, $docs)
    }
    if ($issues.Count -gt 0) {
        Warn ("索引可能过期（" + ($issues -join '；') + "），运行 .\start.ps1 -Reindex")
    } elseif ($docs -ge 0) {
        Ok ("索引较新（kb {0} 篇 / 索引 {1} 篇，构建 {2:yyyy-MM-dd HH:mm}）" -f $info.MdCount, $docs, $info.DbTime)
    } else {
        Ok ("索引时间不早于 kb（构建 {0:yyyy-MM-dd HH:mm}），但无法读取索引文章数" -f $info.DbTime)
    }
}

function Format-FileSize([long]$bytes) {
    if ($bytes -ge 1GB) { return ('{0:N2} GB' -f ($bytes / 1GB)) }
    if ($bytes -ge 1MB) { return ('{0:N2} MB' -f ($bytes / 1MB)) }
    if ($bytes -ge 1KB) { return ('{0:N1} KB' -f ($bytes / 1KB)) }
    return ('{0} B' -f $bytes)
}

# 只读展示：索引 manifest 时间戳 + 最近一次本地备份时间戳。
function Show-DataProtection {
    $manifestPath = Join-Path $Root 'index\manifest.json'
    if (Test-Path -LiteralPath $manifestPath) {
        try {
            $m = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 |
                 ConvertFrom-Json
            $mt = (Get-Item -LiteralPath $manifestPath).LastWriteTime
            $count = -1
            if ($null -ne $m.files) {
                $count = @($m.files.PSObject.Properties).Count
            }
            Ok ("索引清单 manifest: built_at={0}，{1} 篇（文件 {2:yyyy-MM-dd HH:mm}）" -f `
                "$($m.built_at)", $count, $mt)
        } catch {
            Warn "索引清单 manifest 存在但无法读取: $($_.Exception.Message)"
        }
    } else {
        Warn '索引清单 manifest 不存在（运行 .\start.ps1 -Reindex 生成）'
    }

    $backupDir = Join-Path $Root 'backup'
    $latest = $null
    if (Test-Path -LiteralPath $backupDir) {
        $latest = Get-ChildItem -LiteralPath $backupDir -Filter 'ctf_kb_*.zip' `
                  -File -ErrorAction SilentlyContinue |
                  Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }
    if ($latest) {
        Ok ("最近备份: {0}（{1}，{2:yyyy-MM-dd HH:mm}）" -f `
            $latest.Name, (Format-FileSize $latest.Length), $latest.LastWriteTime)
    } else {
        Warn '尚无本地备份（运行 .\backup.ps1 生成）'
    }
}

function Stop-Listening([int]$p, [string]$what) {
    $procId = Get-PortPid $p
    if (-not $procId) { return $false }
    if (-not (Test-ProjectProcess $procId)) {
        Warn ":$p 被 pid=$procId 占用，但命令行不属于本项目，跳过停止（请手动检查）"
        return $false
    }
    try {
        Stop-Process -Id $procId -Force -ErrorAction Stop
    } catch {
        Warn "$what 停止失败 (pid=$procId): $($_.Exception.Message)"
        return $false
    }
    for ($i = 0; $i -lt 20; $i++) {
        if (-not (Get-PortPid $p)) { break }
        Start-Sleep -Milliseconds 200
    }
    $left = Get-PortPid $p
    if ($left) {
        Warn "$what 端口 :$p 仍被 pid=$left 占用（可能需要管理员）"
        return $false
    }
    Ok "$what 已停止 (pid=$procId, :$p)"
    return $true
}

function Stop-PidFile([string]$file, [string]$what) {
    if (-not (Test-Path $file)) { return }
    $text = Get-Content $file -Raw -ErrorAction SilentlyContinue
    if ($null -ne $text) { $text = $text.Trim() }
    if ($text -match '^\d+$') {
        $procId = [int]$text
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            if (Test-ProjectProcess $procId) {
                try {
                    Stop-Process -Id $procId -Force -ErrorAction Stop
                    Ok "$what 记录的外壳进程已停止 (pid=$procId)"
                } catch {
                    Warn "$what 记录进程停止失败 (pid=$procId): $($_.Exception.Message)"
                }
            } else {
                Warn "忽略 $file 中的 pid=$procId（命令行不属于本项目）"
            }
        }
    }
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------- 状态
function Show-Status {
    Say ''
    Say '=== 当前状态 ===' 'Cyan'
    Say '[Web]' 'Cyan'
    Show-WebStatus
    Say '[索引]' 'Cyan'
    Show-IndexStatus
    Show-DataProtection
    Say '[模型]' 'Cyan'
    Show-ModelStatus
    Say ''
}

# ---------------------------------------------------------------- 停止
if ($Stop) {
    Say '' ; Say '=== 停止服务 ===' 'Cyan'
    # 先按真实监听者关闭，再核对 pid 文件里可能残留的外壳进程。
    Stop-Listening $Port 'Web 界面' | Out-Null
    if (-not $NoModel) { Stop-Listening $OllamaPort 'Ollama' | Out-Null }
    Stop-PidFile (Join-Path $LogD 'web.pid') 'Web 界面'
    if (-not $NoModel) { Stop-PidFile (Join-Path $LogD 'llama.pid') 'Qwen3.5 模型服务' }
    if (-not $NoModel) { Stop-PidFile (Join-Path $LogD 'ollama.pid') 'Ollama' }
    Say ''
    if ($NoModel) { Ok '查询服务已停止' } else { Ok '全部停止' }
    return
}

if ($Reindex) {
    Say '' ; Say '=== 重建索引 ===' 'Cyan'
    if (-not (Test-Path $Venv)) {
        Bad "找不到 Python: $Venv"
        return
    }
    $null = Test-KbPython -Root $Root -PythonExe $Venv
    if (-not (Test-Path $CliScript)) {
        Bad "找不到 $CliScript"
        return
    }
    if (Get-PortPid $Port) {
        Warn '后端仍在运行；重建完成后请再执行 .\start.ps1 -Stop 然后 -Start 使新索引生效'
    }
    Push-Location $Root
    try {
        & $Venv $CliScript index
        if ($LASTEXITCODE -eq 0) { Ok '索引重建完成' }
        else { Bad "索引重建失败（退出码 $LASTEXITCODE）" }
    } finally {
        Pop-Location
    }
    return
}

if ($Status) { Show-Status; return }

# -Start 是显式别名：与“直接运行 .\start.ps1（无参数）”走完全相同的启动流程，
# 因此这里不单独分支，继续执行下面的环境检查与服务启动。
if ($Start) { }

# ---------------------------------------------------------------- 环境检查
Say ''
Say '=== 1. 检查环境 ===' 'Cyan'

if (-not (Test-Path $Venv)) {
    Bad "找不到 Python: $Venv"
    Say '  请准备便携环境，或用 -PythonExe 指定已有解释器'
    return
}
$null = Test-KbPython -Root $Root -PythonExe $Venv
Ok ("Python: {0}（{1}）" -f $Venv, $RuntimeChoice.Source)

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
    & $Venv $CliScript index
    Pop-Location
}
Show-IndexFreshness

# ---------------------------------------------------------------- Ollama
Say ''
Say '=== 2. 模型服务 ===' 'Cyan'

$olPid = Get-PortPid $OllamaPort
if ($NoModel -or $Backend -in @('none', 'off')) {
    Ok '仅启动查询界面，不启动生成模型服务'
} elseif ($Backend -eq 'llama_server') {
    $llamaArgs = @($LlamaScript, 'start', '--log-dir', $LogD)
    if ($ChatModel) { $llamaArgs += @('--model', $ChatModel) }
    if ($CpuOnly) { $llamaArgs += '--cpu' }
    & $Venv -X utf8 @llamaArgs
    if ($LASTEXITCODE -ne 0) { Warn '模型服务启动失败，可先使用资料查询；原因见上方提示和日志' }
} elseif ($olPid) {
    Show-ModelStatus
} else {
    if (-not (Test-Path $OlExe)) {
        Bad "找不到 ollama.exe: $OlExe"
        Say '  模型服务不可用，Web 界面可以检索但无法生成建议。'
    } else {
        $env:OLLAMA_MODELS = $OlMod
        try {
            $olArgs = @('serve')
            $sp = Start-Process -FilePath $OlExe -ArgumentList $olArgs `
                  -WorkingDirectory $OlLib `
                  -RedirectStandardOutput (Join-Path $LogD 'ollama.log') `
                  -RedirectStandardError  (Join-Path $LogD 'ollama.err.log') `
                  -WindowStyle Hidden -PassThru
            $sp.Id | Set-Content (Join-Path $LogD 'ollama.pid') -Encoding ASCII

            if (Wait-Http "http://127.0.0.1:$OllamaPort/api/version" 40) {
                $listenPid = 0
                for ($i = 0; $i -lt 20; $i++) {
                    $listenPid = Get-PortPid $OllamaPort
                    if ($listenPid) { break }
                    Start-Sleep -Milliseconds 250
                }
                if ($listenPid) {
                    $listenPid | Set-Content (Join-Path $LogD 'ollama.pid') -Encoding ASCII
                    Ok "已启动 (pid=$listenPid)"
                } else {
                    Warn "未查到 :$OllamaPort 的监听进程，暂记启动器 pid=$($sp.Id)"
                }
                Show-ModelStatus
            } else {
                Bad "Ollama 启动超时（:$OllamaPort）"
                Show-LogTail 'ollama'
                Show-StartupAdvice $OllamaPort
            }
        } catch {
            Bad "Ollama 启动失败: $($_.Exception.Message)"
            Show-LogTail 'ollama'
            Show-StartupAdvice $OllamaPort
        }
    }
}

# ---------------------------------------------------------------- Web 服务
Say ''
Say '=== 3. Web 搜索界面 ===' 'Cyan'

$webPid = Get-PortPid $Port
if ($webPid) {
    Show-WebStatus
} else {
    $env:AGENT_PORT = "$Port"
    $env:AGENT_HOST = '127.0.0.1'
    $env:AGENT_DISABLE_GENERATION = if ($NoModel) { '1' } else { '0' }
    # 模型/host/context 由 config.toml 决定；这里不再硬编码模型名。
    # AGENT_MODEL / AGENT_OLLAMA 只有在用户显式设置时才覆盖配置。
    if ($CpuOnly) { $env:AGENT_OLLAMA = "http://127.0.0.1:$OllamaPort" }

    try {
        Push-Location $Root
        try {
            $sp = Start-Process -FilePath $Venv -ArgumentList @(('"{0}"' -f $Srv)) `
                  -WorkingDirectory $Root `
                  -RedirectStandardOutput (Join-Path $LogD 'web.log') `
                  -RedirectStandardError  (Join-Path $LogD 'web.err.log') `
                  -WindowStyle Hidden -PassThru
        } finally {
            Pop-Location
        }
        $sp.Id | Set-Content (Join-Path $LogD 'web.pid') -Encoding ASCII

        if (Wait-Http "http://127.0.0.1:$Port/api/health" 30) {
            $listenPid = 0
            for ($i = 0; $i -lt 20; $i++) {
                $listenPid = Get-PortPid $Port
                if ($listenPid) { break }
                Start-Sleep -Milliseconds 250
            }
            if ($listenPid) {
                $listenPid | Set-Content (Join-Path $LogD 'web.pid') -Encoding ASCII
                Ok "已启动 (pid=$listenPid)"
            } else {
                Warn "未查到 :$Port 的监听进程，暂记启动器 pid=$($sp.Id)"
            }
            Show-WebStatus
        } else {
            Bad "Web 启动超时（:$Port）"
            Show-LogTail 'web'
            Show-StartupAdvice $Port
            return
        }
    } catch {
        Bad "Web 启动失败: $($_.Exception.Message)"
        Show-LogTail 'web'
        Show-StartupAdvice $Port
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
Say '  .\start.ps1 -Start    启动服务（等同直接运行 .\start.ps1）' 'DarkGray'
Say '  .\start.ps1 -Status   查看三层状态' 'DarkGray'
Say '  .\start.ps1 -Reindex  重建索引' 'DarkGray'
Say '  .\start.ps1 -Stop     停止全部服务' 'DarkGray'
Say '  .\start.ps1 -Stop -NoModel  只停止查询服务' 'DarkGray'
Say ''
} finally {
    if ($ChatModel) {
        if ($null -eq $PreviousChatModel) { Remove-Item -LiteralPath 'Env:\KB_CHAT_MODEL' -ErrorAction SilentlyContinue }
        else { $env:KB_CHAT_MODEL = $PreviousChatModel }
    }
}
