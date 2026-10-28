# 只读脚本工具库（tools/scripts）

本目录把根目录与 `work/` 里散落的题场探针收敛成可复用、可测试的只读工具。
所有脚本遵循同一约定：

- **只读**：只读取本地输入，不写文件、不改数据库、不联网。
- **不执行输入**：不调用 `eval` / `exec` / `compile`，不导入用户代码，
  不运行附件、样本或第三方程序。
- **不自动执行**：脚本只在你显式传入参数时运行；不会扫描目录后自行触发。
- **不做武器化**：只输出结构、特征与命中情况，不生成攻击载荷。
- **输出稳定**：默认人类可读；加 `--json` 输出 JSON，方便测试与管道处理。

需要写盘、解压或动态调试时，请另立明确授权的任务，不要把写操作塞进本目录。

## 脚本清单

### `crypto/rsa_factor_probe.py`

- 用途：RSA 数论只读探针。对给定的 `n` 做小素数试除、位长与余因子检查，
  判断余因子是否（概率）素数；也可单独判断一个数是否概率素数。
- 输入：
  - `--n` 或 `--n-file`：待检查整数（十进制或 `0x` 十六进制）。
  - `--limit`：试除上界，默认 `2000000`。
  - `--check-prime N`：额外判断一个数。
  - `--json`：JSON 输出。
- 输出：`n_bits`、`small_factors`、`cofactor`、`cofactor_bits`、
  `cofactor_probable_prime`、`fully_factored`、`check_prime` 等。
- 对应旧脚本：根目录 `_probe*.py` 的小因子/余因子检查思路。

```powershell
.\.venv\Scripts\python.exe tools\scripts\crypto\rsa_factor_probe.py --n 143 --json
```

### `forensics/zip_inspect.py`

- 用途：ZIP / JAR / APK 只读清单。列出条目、统计顶层目录、查找加密条目，
  按正则检索条目名与可解码文本内容；不解压、不落盘。
- 输入：
  - `--zip PATH`：压缩包路径（必填）。
  - `--top N`：显示前 N 个顶层目录，默认 20。
  - `--grep PATTERN`：名称/内容正则。
  - `--max-bytes N`：单条目读取上限，默认 2 MiB。
  - `--json`：JSON 输出。
- 输出：`entry_count`、`file_count`、`top_dirs`、`encrypted`、
  `name_hits`、`content_hits`。
- 对应旧脚本：根目录 `_jar*.py`（清点 jar 结构）与 `_extract.py`
  （先看清单再决定是否另行授权解压）。

```powershell
.\.venv\Scripts\python.exe tools\scripts\forensics\zip_inspect.py --zip sample.jar --grep flag --json
```

### `misc/filter_probe.py`

- 用途：黑名单过滤只读探针。静态比对候选字符串会命中哪些过滤词，
  报告长度、ASCII、花括号等限制线索；**不执行候选输入**。
- 输入：
  - `--blacklist` 或 `--blacklist-file`：逗号/分号/换行分隔的黑名单。
  - `--payload` 或 `--payload-file`：待检查的候选字符串。
  - `--json`：JSON 输出。
- 输出：`match`、`hit_count`、`hits`、`payload_length`、`is_ascii`、
  `has_braces`、`executed=false`。
- 对应旧脚本：根目录 `_jail_test.py` 的过滤表比对思路，
  但去掉了其中的 `eval` 循环与自动执行。

```powershell
.\.venv\Scripts\python.exe tools\scripts\misc\filter_probe.py --blacklist "eval,exec" --payload "{print(1)}" --json
```

## 公共模块

`_shared.py` 只提供 stdio 编码、`--json` 开关、整数解析与输出格式化，
不包含任何网络、执行或写文件能力。

## 测试

`tests/test_scripts.py` 用临时数据实际运行本目录脚本，校验 JSON 输出与
`read_only` / `executed=false` 标记；不接触真实模型、索引或用户上传内容。
