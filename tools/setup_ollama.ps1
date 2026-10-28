param(
    # 留空则在脚本里按项目位置自动定位，搬目录后不用改这里
    [string]$ModelFile = '',
    [string]$ModelName = 'qwen25-coder-7b-local',
    [int]$Port = 11434,
    [int]$NumCtx = 8192,
    [switch]$Recreate,
    [switch]$Stop
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

$Root      = Split-Path -Parent $PSScriptRoot
$ServerDir = Join-Path $Root 'models\ollama-server'
$Exe       = Join-Path $ServerDir 'ollama.exe'
$ModelsDir = Join-Path $Root 'models\ollama-models'
$PidFile   = Join-Path $ServerDir 'ollama.pid'
$LogFile   = Join-Path $ServerDir 'ollama.log'
$ErrLog    = Join-Path $ServerDir 'ollama.err.log'
$ApiHost   = "127.0.0.1:$Port"
$Api       = "http://$ApiHost"

# 默认模型文件按项目位置自动定位（搬盘后无需改脚本）
if ([string]::IsNullOrWhiteSpace($ModelFile)) {
    $ModelFile = Join-Path $Root 'models\gguf\qwen2.5-coder-7b-instruct-q4_k_m.gguf'
}

function Say([string]$m) { Write-Host $m }

# 注意: ollama 的 runtimes ({exe}\..\lib\ollama\<accel>) 相对 **exe 所在目录** 解析,
# 所以 WorkingDirectory 必须是 lib\ollama (或 exe 的上一级), 否则找不到 ggml-cuda.dll。
$env:OLLAMA_MODELS          = $ModelsDir
$env:OLLAMA_HOST            = $ApiHost
$env:OLLAMA_NO_CLOUD        = '1'
$env:OLLAMA_FLASH_ATTENTION = '1'
$env:OLLAMA_KV_CACHE_TYPE   = 'q8_0'

New-Item -ItemType Directory -Force -Path $ModelsDir, $ServerDir | Out-Null

function Get-ListeningPid {
    $c = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($c) { return $c[0].OwningProcess }
    return $null
}

function Stop-Server {
    $p = Get-ListeningPid
    if ($p) {
        Say "stopping ollama serve (pid $p)"
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    Remove-Item $PidFile -ErrorAction SilentlyContinue
}

if ($Stop) { Stop-Server; Say 'stopped'; return }

if (-not (Test-Path $Exe)) { throw "ollama.exe not found: $Exe" }
# GGUF 源文件只用于首次导入。如果模型已经在 ollama-models 里，
# 删掉 gguf 副本不影响启动——这时只跳过导入步骤，不要直接报错。
$NeedImport = Test-Path $ModelFile
if (-not $NeedImport) {
    Say "  [提示] 本地 GGUF 不存在，跳过导入（直接使用已导入的模型）"
    Say "         如要重新导入，请先把 GGUF 放回: $ModelFile"
}

# ---------------------------------------------------------------- 1. 启动
Say '=== 1. ollama serve ==='
$listenPid = Get-ListeningPid
if ($listenPid) {
    Say "  已在运行, pid=$listenPid"
    $listenPid | Set-Content -Path $PidFile -Encoding ASCII
} else {
    Say "  启动中 ($Api) ..."
    $sp = Start-Process -FilePath $Exe -ArgumentList 'serve' `
        -WorkingDirectory (Join-Path $ServerDir 'lib\ollama') `
        -RedirectStandardOutput $LogFile -RedirectStandardError $ErrLog `
        -WindowStyle Hidden -PassThru
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Milliseconds 500
        $listenPid = Get-ListeningPid
        if ($listenPid) { break }
    }
    if (-not $listenPid) { throw "ollama 未能在 $Port 上监听, 见 $ErrLog" }
    $listenPid | Set-Content -Path $PidFile -Encoding ASCII
    Say "  已启动, pid=$listenPid (spawn=$($sp.Id))"
}

# 等 API 就绪
$ready = $false
for ($i = 0; $i -lt 80; $i++) {
    Start-Sleep -Milliseconds 500
    $code = & curl.exe -s -o NUL -w '%{http_code}' --max-time 3 "$Api/api/version"
    if ($code -eq '200') { $ready = $true; break }
}
if (-not $ready) { throw "API 未就绪: $Api" }
Say "  API ready (pid=$(Get-ListeningPid), port=$Port)"

# 确认 GPU 被识别
$gpuLines = Select-String -Path $ErrLog -Pattern 'inference compute' -ErrorAction SilentlyContinue |
    Select-Object -Last 1
if ($gpuLines) { Say ("  engine: " + ($gpuLines.Line -replace '.*description=', '')) }
else { Say '  (日志中未见 inference compute 行, 可能回退 CPU)' }

# ---------------------------------------------------------------- 2. 导入模型
Say ''
if ($NeedImport) {
Say '=== 2. 导入本地 GGUF (不重新下载) ==='
$mfPath = Join-Path $ServerDir 'Modelfile'
$modelAbs = (Resolve-Path -LiteralPath $ModelFile).Path
$mfText = "FROM $modelAbs`nPARAMETER num_ctx $NumCtx`nPARAMETER temperature 0.2`n"
[System.IO.File]::WriteAllText($mfPath, $mfText, (New-Object System.Text.UTF8Encoding($false)))
Say "  Modelfile -> $mfPath"
Say ($mfText.TrimEnd())

$tags = & curl.exe -s -m 10 "$Api/api/tags"
$exists = $tags -match [regex]::Escape($ModelName)
if ($exists -and -not $Recreate) {
    Say "  模型已存在: $ModelName (用 -Recreate 重建)"
} else {
    # 关键: ollama create 必须 cwd=exe 目录, 且 -f 用绝对路径, 否则报
    #       "no Modelfile or safetensors files found"
    Push-Location $ServerDir
    & $Exe create $ModelName -f $mfPath *> $null
    $ec = $LASTEXITCODE
    Pop-Location
    Say "  create exit=$ec"
}
}   # end if ($NeedImport)

# ---------------------------------------------------------------- 3. 验证
Say ''
Say '=== 3. 生成验证 & 显存 ==='
$body = '{"model":"' + $ModelName + '","prompt":"Explain in two sentences how a ROP chain bypasses NX.","stream":false,"options":{"num_predict":64,"temperature":0}}'
$btmp = Join-Path $env:TEMP 'ollama_verify.json'
$otmp = Join-Path $env:TEMP 'ollama_verify.out.json'
[System.IO.File]::WriteAllText($btmp, $body, (New-Object System.Text.UTF8Encoding($false)))

$baseVram = [int](& nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | Select-Object -First 1)
$job = Start-Job -ScriptBlock {
    param($u, $f, $o) & curl.exe -s -m 900 -X POST $u -H 'Content-Type: application/json' --data-binary "@$f" -o $o
} -ArgumentList "$Api/api/generate", $btmp, $otmp
$samples = @()
while ($job.State -eq 'Running') {
    $samples += [int](& nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | Select-Object -First 1)
    Start-Sleep -Milliseconds 400
}
Receive-Job $job -Wait -AutoRemoveJob | Out-Null
$samples += [int](& nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | Select-Object -First 1)

$j = Get-Content $otmp -Raw -ErrorAction SilentlyContinue | ConvertFrom-Json
if ($j -and -not $j.error) {
    $ed = [double]$j.eval_duration / 1e9
    Say ("  {0} tokens in {1:N2}s -> {2:N2} tok/s" -f $j.eval_count, $ed, ([double]$j.eval_count / $ed))
    $ps = (& curl.exe -s -m 10 "$Api/api/ps") | ConvertFrom-Json
    if ($ps.models -and $ps.models.Count -gt 0) {
        $m0 = $ps.models[0]
        Say ("  model_vram={0} MB / total {1} MB  ctx={2}" -f [math]::Round($m0.size_vram / 1MB, 1), [math]::Round($m0.size / 1MB, 1), $m0.context_length)
    }
} else {
    Say ("  生成失败: " + $(if ($j) { $j.error } else { 'no response' }))
}
Say ("  nvidia-smi: baseline={0} MiB, peak={1} MiB" -f $baseVram, (($samples | Measure-Object -Maximum).Maximum))
Say ''
Say "PID=$listenPid  PORT=$Port  MODEL=$ModelName"
Say '用法:  curl http://127.0.0.1:11434/api/tags'
Say "停止:  .\tools\setup_ollama.ps1 -Stop"
