# CTF 知识库 本地数据备份
#
#   .\backup.ps1              打包关键本地数据到 backup\ctf_kb_YYYYMMDD_HHMMSS.zip
#   .\backup.ps1 -Keep 3      只保留最近 3 份（默认）
#
# 包含：kb\_imported\、kb\_imported_cats\、index\（含 graph.db）、
#       work\workspaces\、work\feedback\（反馈 JSONL）。
# 不包含：kb\ 其他手写文档（已在 Git 中）、models\、work\attachments\
#         （附件副本可能很大，可另行自行备份）、日志与构建产物。
#
# 只使用 Windows 自带 Compress-Archive，不引入 7z 等外部依赖。

param(
    [int]$Keep = 3
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$BackupDir = Join-Path $Root 'backup'

if ($Keep -lt 1) { $Keep = 1 }
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

function Say($m, $c = 'Gray') { Write-Host $m -ForegroundColor $c }
function Ok  ($m) { Say "  [OK]   $m" 'Green' }
function Warn($m) { Say "  [警告] $m" 'Yellow' }
function Bad ($m) { Say "  [失败] $m" 'Red' }

function Format-Size([long]$bytes) {
    if ($bytes -ge 1GB) { return ('{0:N2} GB' -f ($bytes / 1GB)) }
    if ($bytes -ge 1MB) { return ('{0:N2} MB' -f ($bytes / 1MB)) }
    if ($bytes -ge 1KB) { return ('{0:N1} KB' -f ($bytes / 1KB)) }
    return ('{0} B' -f $bytes)
}

$sources = @(
    @{ Path = (Join-Path $Root 'kb\_imported');      Dst = 'kb\_imported' },
    @{ Path = (Join-Path $Root 'kb\_imported_cats'); Dst = 'kb\_imported_cats' },
    @{ Path = (Join-Path $Root 'index');          Dst = 'index' },
    @{ Path = (Join-Path $Root 'work\workspaces'); Dst = 'work\workspaces' },
    @{ Path = (Join-Path $Root 'work\feedback');  Dst = 'work\feedback' }
)

$existing = @()
foreach ($s in $sources) {
    if (Test-Path -LiteralPath $s.Path) {
        $existing += $s
    } else {
        Warn ("跳过不存在的目录: {0}" -f $s.Dst)
    }
}

Say ''
Say '=== 备份本地数据 ===' 'Cyan'
if ($existing.Count -eq 0) {
    Bad '没有任何可备份的数据目录，未生成压缩包'
    exit 1
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$zip = Join-Path $BackupDir ("ctf_kb_{0}.zip" -f $stamp)
if (Test-Path -LiteralPath $zip) {
    Bad "目标文件已存在: $zip（请稍后重试）"
    exit 1
}

# 先在 backup\.staging_* 下复制一份：index\graph.db 等可能正被 Web 服务打开，
# Compress-Archive 直接读会拿不到共享句柄；Copy-Item 取只读副本成功率高。
$staging = Join-Path $BackupDir (".staging_{0}" -f $stamp)
New-Item -ItemType Directory -Force -Path $staging | Out-Null

Say ("  源目录: {0}" -f (($existing | ForEach-Object { $_.Dst }) -join ', '))
Say ("  输出:   {0}" -f $zip)

try {
    foreach ($s in $existing) {
        $dst = Join-Path $staging $s.Dst
        $parent = Split-Path -Parent $dst
        if (-not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }
        Copy-Item -LiteralPath $s.Path -Destination $dst -Recurse -Force -ErrorAction Stop
    }
    Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zip `
                     -CompressionLevel Optimal -ErrorAction Stop
} catch {
    Bad ("备份失败: {0}" -f $_.Exception.Message)
    if (Test-Path -LiteralPath $zip) {
        try { Remove-Item -LiteralPath $zip -Force -ErrorAction Stop } catch { }
    }
    exit 1
} finally {
    if (Test-Path -LiteralPath $staging) {
        try { Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction Stop } catch { }
    }
}

if (-not (Test-Path -LiteralPath $zip)) {
    Bad '备份失败: 未生成压缩包'
    exit 1
}

$zipItem = Get-Item -LiteralPath $zip
Ok ("已生成 {0}（{1}）" -f $zipItem.Name, (Format-Size $zipItem.Length))

# 只清理本脚本生成的文件，保留最近 $Keep 份。
$all = @(Get-ChildItem -LiteralPath $BackupDir -Filter 'ctf_kb_*.zip' -File |
         Sort-Object LastWriteTime -Descending)
$removed = @()
if ($all.Count -gt $Keep) {
    $removed = @($all | Select-Object -Skip $Keep)
    foreach ($f in $removed) {
        try {
            Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
            Warn ("已删除较旧备份: {0}" -f $f.Name)
        } catch {
            Warn ("删除较旧备份失败 {0}: {1}" -f $f.Name, $_.Exception.Message)
        }
    }
}

$remaining = @(Get-ChildItem -LiteralPath $BackupDir -Filter 'ctf_kb_*.zip' -File |
               Sort-Object LastWriteTime -Descending)
Say ''
Say ("=== 最近备份（保留 {0} 份）===" -f $Keep) 'Cyan'
$total = 0L
foreach ($f in $remaining) {
    $total += $f.Length
    Say ("  {0}  {1,10}  {2:yyyy-MM-dd HH:mm}" -f $f.Name, (Format-Size $f.Length), $f.LastWriteTime)
}
Say ("  合计: {0} 份 / {1}" -f $remaining.Count, (Format-Size $total))
Say ''
