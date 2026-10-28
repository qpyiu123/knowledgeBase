<#
.SYNOPSIS
    CTF 知识库 — 环境一键安装 (Windows 11 / PowerShell 7)

.DESCRIPTION
    幂等地:
      1. 创建/复用 .venv (默认 C:\Python314\python.exe, Python 3.14)
      2. 安装依赖 (清华 PyPI 镜像)
         - huggingface_hub / requests / pyyaml / numpy / sqlite-vec
         - llama-cpp-python: Python 3.14 在 PyPI 没有 wheel, 必须走 abetlen 的 wheel 索引
         - onnxruntime + tokenizers: 零 torch 的 ONNX 嵌入后端
         - sentence-transformers 标为可选 (拖 ~2.5GB torch, 3.14 上通常失败), 默认跳过
      3. 调用 tools\fetch_models.py 下载模型 (幂等, 已存在则跳过)

.PARAMETER Mirror
    强制通过 hf-mirror.com 下载模型

.PARAMETER SkipModels
    只装环境, 不下载模型

.PARAMETER WithTorch
    额外尝试 sentence-transformers (体积大, 失败不阻塞)

.PARAMETER TryCuda
    尝试用 CUDA 源码编译 llama-cpp-python (需 CUDA Toolkit nvcc + VS C++ 工具链)

.PARAMETER Ollama
    额外调用 tools\setup_ollama.ps1 启动 Ollama 并导入 7B 模型 (GPU 路线)

.EXAMPLE
    pwsh -File tools\setup_env.ps1
    pwsh -File tools\setup_env.ps1 -Mirror
    pwsh -File tools\setup_env.ps1 -Ollama
#>
[CmdletBinding()]
param(
    [switch]$Mirror,
    [switch]$SkipModels,
    [switch]$WithTorch,
    [switch]$TryCuda,
    [switch]$Ollama,
    [string]$PythonExe = 'C:\Python314\python.exe'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ---------------------------------------------------------------- 路径
$Root     = Split-Path -Parent $PSScriptRoot
$Venv     = Join-Path $Root '.venv'
$VenvPy   = Join-Path $Venv 'Scripts\python.exe'
$Models   = Join-Path $Root 'models'
$Tools    = Join-Path $Root 'tools'

$PipIndex      = 'https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple'
$LlamaWheelIdx = 'https://abetlen.github.io/llama-cpp-python/whl/cpu'

function Write-Step([string]$msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok([string]$msg)   { Write-Host "  [OK]   $msg" -ForegroundColor Green }
function Write-Warn2([string]$msg){ Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Err2([string]$msg) { Write-Host "  [ERR]  $msg" -ForegroundColor Red }

# 注意: PowerShell 里 "X(...)" 会被当成函数调用, 所以 **不能** 写
#   $v = (& $py -c "...")      <- 语法错误
# 必须用 $v = & $py -c "..." 或 @(...) 收集
function Get-PyOut {
    param([string[]]$PyArgs)
    return & $VenvPy -c $PyArgs[1] 2>$null
}
function Test-PyModule {
    param([string]$Name)
    & $VenvPy -c "import $Name" 2>$null
    return ($LASTEXITCODE -eq 0)
}

Write-Host 'CTF knowledge base — 环境安装' -ForegroundColor Magenta
Write-Host "  ROOT   : $Root"
Write-Host "  VENV   : $Venv"
Write-Host "  PYTHON : $PythonExe"

# ---------------------------------------------------------------- 1. venv
Write-Step '1/4 虚拟环境'
if (Test-Path $VenvPy) {
    $v = Get-PyOut @('-c', 'import sys; print(sys.version.split()[0])')
    Write-Ok "复用已有 venv (Python $v)"
} else {
    if (-not (Test-Path $PythonExe)) {
        Write-Err2 "找不到 $PythonExe, 请用 -PythonExe 指定解释器"
        exit 1
    }
    Write-Host '  创建 venv ...'
    & $PythonExe -m venv $Venv
    if ($LASTEXITCODE -ne 0) { Write-Err2 'venv 创建失败'; exit 1 }
    Write-Ok "venv 已创建: $Venv"
}

$env:PYTHONIOENCODING = 'utf-8'
$env:PIP_DISABLE_PIP_VERSION_CHECK = '1'
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'

& $VenvPy -m pip install -q --upgrade pip 2>&1 | Out-Null

# ---------------------------------------------------------------- 2. 基础依赖
Write-Step '2/4 基础依赖'
$base = @('numpy', 'requests', 'pyyaml', 'huggingface_hub', 'sqlite-vec')
Write-Host "  pip install $($base -join ' ')  (index: $PipIndex)"
& $VenvPy -m pip install -q --only-binary=:all: -i $PipIndex @base 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warn2 '有包无 cp314 wheel (通常是 sqlite-vec), 单独重试其余包'
    & $VenvPy -m pip install -q --only-binary=:all: -i $PipIndex numpy requests pyyaml huggingface_hub 2>&1 | Out-Null
}
foreach ($m in @('numpy', 'requests', 'huggingface_hub', 'yaml')) {
    if (Test-PyModule $m) { Write-Ok "import $m" } else { Write-Err2 "import $m 失败" }
}
if (Test-PyModule 'sqlite_vec') { Write-Ok 'import sqlite_vec' }
else { Write-Warn2 'sqlite-vec 不可用 (numpy 暴力余弦降级即可, 不阻塞)' }

# ---------------------------------------------------------------- 3. llama-cpp-python
Write-Step '3/4 llama-cpp-python'
$hasLlama = Test-PyModule 'llama_cpp'
if ($hasLlama) {
    $ver = Get-PyOut @('-c', 'import llama_cpp; print(llama_cpp.__version__)')
    Write-Ok "已安装 llama_cpp $ver"
} else {
    Write-Host '  首次尝试: 清华镜像 (PyPI) ...'
    & $VenvPy -m pip install -q --only-binary=:all: -i $PipIndex llama-cpp-python 2>&1 | Out-Null
    $hasLlama = Test-PyModule 'llama_cpp'
    if (-not $hasLlama) {
        Write-Warn2 'PyPI 无 cp314 wheel — 改用 abetlen 官方 wheel 索引'
        & $VenvPy -m pip install --only-binary=:all: -i $PipIndex --extra-index-url $LlamaWheelIdx llama-cpp-python 2>&1 | Out-Null
        $hasLlama = Test-PyModule 'llama_cpp'
    }
    if ($hasLlama) {
        $ver = Get-PyOut @('-c', 'import llama_cpp; print(llama_cpp.__version__)')
        Write-Ok "llama_cpp $ver 安装成功"
    } else {
        Write-Err2 'llama-cpp-python 安装失败'
    }
}

# ---- 可选: CUDA 源码编译 ----
if ($TryCuda -and $hasLlama) {
    $gpu = Get-PyOut @('-c', 'import llama_cpp; print(llama_cpp.llama_supports_gpu_offload())')
    if ($gpu -eq 'True') {
        Write-Ok '当前构建已支持 GPU offload, 跳过 CUDA 重编译'
    } else {
        $nvcc = Get-Command nvcc -ErrorAction SilentlyContinue
        $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
        $vsOk = $false
        if (Test-Path $vswhere) {
            $vsPath = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null
            $vsOk = [bool]$vsPath
        }
        Write-Host ("  nvcc={0}  vc_tools={1}" -f [bool]$nvcc, $vsOk)
        if ($nvcc -and $vsOk) {
            Write-Host '  使用 CUDA 编译 llama-cpp-python (10-20 分钟) ...'
            $env:CMAKE_ARGS = '-DGGML_CUDA=on'
            $env:FORCE_CMAKE = '1'
            & $VenvPy -m pip install --no-cache-dir --force-reinstall --upgrade -i $PipIndex llama-cpp-python 2>&1 | Out-Null
            Remove-Item Env:\CMAKE_ARGS, Env:\FORCE_CMAKE -ErrorAction SilentlyContinue
            $gpu = Get-PyOut @('-c', 'import llama_cpp; print(llama_cpp.llama_supports_gpu_offload())')
            if ($gpu -eq 'True') { Write-Ok 'CUDA 编译成功 — n_gpu_layers 现在生效' }
            else { Write-Warn2 'CUDA 编译未生效, 继续使用 CPU 构建' }
        } else {
            Write-Warn2 '缺少 CUDA Toolkit (nvcc) 或 VS C++ 工具链 — 跳过 CUDA 编译'
            Write-Warn2 '本机为纯 CPU 构建; bench_gguf.py 中 n_gpu_layers>0 会被静默忽略'
        }
    }
}

# ---- 可选: sentence-transformers ----
if ($WithTorch) {
    Write-Step '可选: sentence-transformers (会拉 ~2.5GB torch)'
    & $VenvPy -m pip install -q --only-binary=:all: -i $PipIndex sentence-transformers torch 2>&1 | Out-Null
    if (Test-PyModule 'sentence_transformers') { Write-Ok 'sentence_transformers 可用' }
    else { Write-Warn2 'sentence-transformers 安装失败 — 请改用 ONNX / GGUF 嵌入后端' }
}

# ---- 零 torch 的 ONNX 嵌入后端 ----
Write-Step '嵌入后端 (零 torch): onnxruntime + tokenizers'
& $VenvPy -m pip install -q --only-binary=:all: -i $PipIndex onnxruntime tokenizers 2>&1 | Out-Null
if (Test-PyModule 'onnxruntime') {
    $ort = Get-PyOut @('-c', 'import onnxruntime; print(onnxruntime.__version__)')
    Write-Ok "onnxruntime $ort + tokenizers"
} else {
    Write-Warn2 'onnxruntime 不可用 — 嵌入回退到 llama.cpp 加载 BGE GGUF'
}

# ---------------------------------------------------------------- 4. 模型
Write-Step '4/4 模型下载'
New-Item -ItemType Directory -Force -Path $Models, (Join-Path $Models 'gguf') | Out-Null
$fetch = Join-Path $Tools 'fetch_models.py'
if ($SkipModels) {
    Write-Ok '已跳过 (-SkipModels)'
} elseif (-not (Test-Path $fetch)) {
    Write-Err2 "找不到 $fetch"
} else {
    $fargs = @('-u', $fetch)
    if ($Mirror) { $fargs += '--mirror' }
    & $VenvPy $fetch
    if ($LASTEXITCODE -eq 0) { Write-Ok '模型全部就绪' }
    else { Write-Warn2 "fetch_models 返回 $LASTEXITCODE — 复核: python tools\fetch_models.py --check" }
}

# ---------------------------------------------------------------- 自检
Write-Step '自检'
& $VenvPy -m pip list 2>$null | Select-String -Pattern 'llama|numpy|huggingface|onnx|tokenizers|sqlite|requests|yaml|torch|sentence'
Write-Host ''
if ($hasLlama) {
    $gpu = Get-PyOut @('-c', 'import llama_cpp; print(llama_cpp.llama_supports_gpu_offload())')
    Write-Host "  llama_supports_gpu_offload() = $gpu" -ForegroundColor Magenta
    if ($gpu -ne 'True') {
        Write-Host '  (False = 纯 CPU 构建, GPU 层卸载不可用; 需要 GPU 请走 Ollama 路线)' -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------- 可选: Ollama
if ($Ollama) {
    $setupOllama = Join-Path $Tools 'setup_ollama.ps1'
    if (Test-Path $setupOllama) {
        Write-Step 'Ollama (GPU 路线)'
        & pwsh -NoProfile -File $setupOllama
    } else {
        Write-Warn2 "找不到 $setupOllama"
    }
}

Write-Host "`n完成。下一步:" -ForegroundColor Green
Write-Host '  .\.venv\Scripts\python.exe tools\bench_gguf.py'
Write-Host '  .\tools\setup_ollama.ps1   (GPU 推理)'
Write-Host ''
