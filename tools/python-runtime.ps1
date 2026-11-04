# 解释器选择无需预先安装系统 Python。
function Resolve-KbPython {
    param([string]$Root, [string]$PythonExe = '')
    $configured = 'auto'
    $section = ''
    $config = Join-Path $Root 'config.toml'
    if (Test-Path -LiteralPath $config) {
        foreach ($line in (Get-Content -LiteralPath $config -Encoding UTF8)) {
            if ($line -match '^\s*\[([^\]]+)\]') { $section = $Matches[1]; continue }
            if ($section -eq 'runtime' -and $line -match '^\s*python\s*=\s*("(?:[^"\\]|\\.)*"|''[^'']*'')\s*(?:#.*)?$') {
                $value = $Matches[1]
                if ($value.StartsWith('"')) { $configured = $value | ConvertFrom-Json }
                else { $configured = $value.Substring(1, $value.Length - 2) }
            }
        }
    }
    $choice = $PythonExe
    $source = 'parameter'
    if (-not $choice) { $choice = $env:KB_PYTHON; $source = 'KB_PYTHON' }
    if (-not $choice -and $configured -and $configured -ne 'auto') { $choice = $configured; $source = 'config.toml' }
    if ($choice) {
        if (-not [IO.Path]::IsPathRooted($choice)) {
            $local = Join-Path $Root $choice
            if (Test-Path -LiteralPath $local -PathType Leaf) { $choice = $local }
            else {
                $command = Get-Command -Name $choice -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($command) { $choice = $command.Source } else { $choice = $local }
            }
        }
        if (-not (Test-Path -LiteralPath $choice -PathType Leaf)) { throw "$source 指定的 Python 不存在：$choice" }
        return [PSCustomObject]@{ Path = [IO.Path]::GetFullPath($choice); Source = $source }
    }
    foreach ($relative in @('runtime\python-portable\python.exe', '.venv\Scripts\python.exe')) {
        $candidate = Join-Path $Root $relative
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
        try { $version = & $candidate -I -c 'import sys;print(sys.version_info >= (3,11))' 2>$null }
        catch { continue }
        if ($LASTEXITCODE -eq 0 -and "$version".Trim() -eq 'True') {
            return [PSCustomObject]@{ Path = $candidate; Source = 'auto' }
        }
    }
    throw '找不到可运行的 Python 3.11+，请准备便携环境，或用 -PythonExe / KB_PYTHON 指定解释器'
}

function Test-KbPython {
    param([string]$Root, [string]$PythonExe)
    $previousEncoding = [Console]::OutputEncoding
    try {
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
        $raw = & $PythonExe -I (Join-Path $Root 'tools\python_runtime.py') --probe
    } finally { [Console]::OutputEncoding = $previousEncoding }
    if (-not $raw) { throw "Python 无法运行：$PythonExe" }
    $report = ($raw -join "`n") | ConvertFrom-Json
    if (-not $report.ok) {
        $missing = @($report.missing | ForEach-Object { $_.module }) -join ', '
        throw "Python 环境不可用：$PythonExe；缺少依赖：$missing；需要 Python 3.11+ 和 SQLite FTS5"
    }
    return $report
}
