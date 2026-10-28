---
title: shell 与脚本一行流（awk/sed/grep/perl 提取比赛数据）
category: misc
tags: [shell, awk, sed, grep, regex, oneliner]
signals: [题目给了一个巨大的日志或者 csv 让你统计某个字段, 需要从几千行输出里提取符合格式的字符串, 题目要求把十六进制 dump 还原成文件, 给的是一个超大的文本里藏着按规律排列的 flag 字符, 需要在 Linux 环境里快速处理而不是写 python, 题目要提交的是某个统计数字或者排序结果, 数据量达到几百兆 python 读一遍都很慢]
difficulty: easy
source: "GNU awk 手册 / GNU sed 手册 / POSIX 正则规范 / Perl 正则文档"
tools: [awk, sed, grep, perl, xargs, python]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.log`、`.csv`、`.txt`，几万行，题目问"出现次数最多的 IP 是什么"。
- 题目给出的是一段程序的输出（`stdout` 存成文件），需要从**大量类似行**里挑出异常行。
- 十六进制 dump 的文本（`xxd` 输出格式）需要还原成二进制。
- flag 的字符被**按列分散**在每一行相同的位置上。
- 数据量很大（>100MB），用编辑器打不开。
- 题目提示"可以用 Linux 命令试试"。

## 二、原理

- **管道 = 流式处理**：`grep` 过滤 → `sed` 替换 → `awk` 分列聚合 → `sort | uniq -c | sort -rn`，几乎能覆盖 90% 的数据清理题。
- **awk 的模型**：`pattern { action }`，内置变量 `NR`（行号）、`NF`（字段数）、`FS/OFS`（分隔符），`END{}` 做汇总。
- **sed 的模型**：按行做 `s///` 替换与 `p/d` 选行，`-E` 开扩展正则，`-n` 只打印显式命中的行。
- **grep -P**：PCRE 语法，支持 `\d`、`\b`、`(?<=...)` 后行断言，比 BRE 强大得多。
- **perl -ne**：真正的正则引擎 + 自动循环读行（`$_`），一行流最强的工具。

## 三、操作步骤

1. **先看数据形态**：`head -5`、`wc -l`、`file`，判断分隔符与编码。
2. **定位行**：`grep -n` 加关键字缩小范围。
3. **提取**：`grep -oP` 或 `awk -F` 切字段，`sed` 清理多余字符。
4. **聚合**：`sort | uniq -c | sort -rn | head`。
5. **还原**：`xxd -r` / `printf` / `sed 's/ //g'` 拼回二进制。
6. **校验**：小样本用 python 复算一遍，确保命令结果可信。

## 四、命令 / 脚本

```bash
# —— 通用清理 ——
sed -i 's/\r$//' data.txt                 # 去 Windows 换行
awk 'NF' data.txt > clean.txt             # 去空行
grep -oP 'flag\{[^}]+\}' all.txt | head   # 提取所有 flag
grep -c 'ERROR' app.log                   # 计数

# —— 统计 ——
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10   # top IP
awk -F'\t' '$5 > 500 {print $2, $5}' data.tsv                       # 条件筛选
awk '{s+=$3} END {print s, NR, s/NR}' nums.txt                      # 求和/均值
awk '!seen[$0]++' dup.txt                                           # 去重保序

# —— 正则提取（PCRE） ——
grep -oP '(?<=user=)[^&]+' urls.txt
grep -oP '\b\d{1,3}(\.\d{1,3}){3}\b' log.txt | sort -u
perl -ne 'print "$1\n" if /flag\{([^}]+)\}/' data.txt

# —— 十六进制还原 ——
xxd -r dump.hex > out.bin
xxd -r -p plainhex.txt > out.bin            # 无地址栏的纯 hex
sed 's/0x//g; s/,//g' bytes.txt | xxd -r -p > out.bin
printf '%b' "$(sed 's/\\x/ /g' raw.txt | tr ' ' '\\')" > out.bin 2>/dev/null

# —— 按列取字符（每行第 k 个字符拼成串） ——
awk '{printf "%s", substr($0,7,1)} END{print ""}' lines.txt
cut -c7 lines.txt | tr -d '\n'; echo

# —— 大文件并行 ——
find . -name '*.log' -print0 | xargs -0 -P8 grep -l 'flag{'
```

```bash
# 从 nc 输出里一路提取（典型 misc 链路）
cat raw.txt \
  | tr -d '\r' \
  | sed -n '/BEGIN/,/END/p' \
  | grep -oP '[A-Za-z0-9+/=]{20,}' \
  | base64 -d 2>/dev/null | strings
```

```python
#!/usr/bin/env python3
# 用 python 复核 shell 统计结果（给"命令跑出来靠谱吗"一个交叉验证）
import collections, re, sys

ips = collections.Counter()
pat = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})\b')
for line in open('access.log', encoding='utf-8', errors='replace'):
    m = pat.search(line)
    if m:
        ips[m.group(1)] += 1
for ip, c in ips.most_common(10):
    print(c, ip)
```

## 五、常见坑 / 变体

- **`grep -P` 不可用**：macOS 自带 BSD grep 没有 `-P`，用 `ggrep` 或 perl 代替。
- **列错位**：`awk` 默认 `FS` 是"空白序列"，若数据用制表符或连续空格会切错，显式 `-F'\t'`。
- **`sort -n` vs `sort -h`**：带 `K/M/G` 的单位要用 `-h`，否则按字符串排。
- **`uniq` 必须先排序**：不排序只去相邻重复。
- **超大文件内存**：`sort` 默认走临时文件，加 `-S 2G` 提速；`awk` 的关联数组会吃内存，超千万行改用 `sort | uniq`。
- **xxd 格式的偏移列**：`xxd -r` 会自动跳过地址列，但**纯 hex 文本**要加 `-p`，否则把 `dead` 当偏移量解析。
- **不可见字符**：提取出的串里可能有 `\u200b` 零宽空格，用 `sed 's/\xe2\x80\x8b//g'` 清理。
- **变体**：`jq` 处理 JSON、`csvkit` 处理 CSV、`tsv` 大文件用 `mlr`（Miller）。

## 六、进阶：把命令链写进脚本模板

比赛里反复出现的清理动作，建议固化成一个小脚本，避免每次重新想参数：

```bash
#!/usr/bin/env bash
# clean.sh：通用清理 + 提取 + 汇总
set -euo pipefail
IN="${1:?usage: clean.sh <file>}"

# 1) 统一编码与换行
iconv -f UTF-8 -t UTF-8 -c "$IN" 2>/dev/null || cat "$IN"
```

```bash
# 2) 提取所有可疑长串（base64 风格）
grep -oE '[A-Za-z0-9+/=]{24,}' data.txt | sort -u | head -30
# 3) 找十六进制块
grep -oE '([0-9a-fA-F]{2}){16,}' data.txt | head -10
# 4) 找条码/坐标/日期
grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:]{8}' data.txt | sort | uniq -c | sort -rn | head
```

```bash
# 5) 统计每个字段的分布（TSV）
awk -F'\t' '{c[$3]++} END {for (k in c) print c[k], k}' data.tsv | sort -rn | head -20
# 6) 找出"唯一异常行"：某字段与本列众数不同的行
awk -F',' 'NR==FNR {c[$4]++; n[$4]=$0; next} {m[$4]++} END {}' data.csv /dev/null
```

```bash
# 7) 按固定偏移取字节（二进制 dump 里定位 flag）
dd if=image.raw bs=1 skip=$((0x1a2b)) count=64 2>/dev/null | xxd
# 8) 在超大二进制里搜索并打印上下文
grep -aboP 'flag\{' image.raw | while IFS=: read -r off rest; do
  dd if=image.raw bs=1 skip=$off count=60 2>/dev/null; echo
done
```

```bash
# 9) 批量把 n 个文件首 16 字节打出来做指纹归类
for f in *; do printf '%-30s ' "$f"; xxd -l 8 -p "$f"; done | sort -k2
# 10) 并发跑命令（8 路）
ls *.log | xargs -P8 -I{} sh -c 'echo "== {}"; grep -m1 -o "flag{[^}]*}" "{}"' 2>/dev/null
```

```bash
# 11) perl 一行流：一次完成"去重 + 计数 + 排序"
perl -ne 'chomp; $c{$_}++ if /^[0-9a-f]{32}$/; END { print "$c{$_} $_\n" for sort { $c{$b} <=> $c{$a} } keys %c }' hashes.txt
# 12) sed 多文件原地改
find . -name '*.txt' -exec sed -i -E 's/[[:space:]]+$//' {} +
```

**性能提示**：`awk` 比 `python` 处理纯文本快 3~10 倍，但一旦涉及复杂解析（JSON、protobuf）就别硬撑，直接 `python -c` 加流式 `for line in open(...)`，内存占用同样是常数级。

**可复现性**：把最终跑通的命令按顺序写进 `solve.sh` 并附输出，比赛后的 WP 直接用它验证——这比贴截图更可信。

## 六、参考来源

- [GNU awk 官方手册（字段、内置变量与模式动作）](https://www.gnu.org/software/gawk/manual/gawk.html)
- [GNU sed 官方手册](https://www.gnu.org/software/sed/manual/sed.html)
- [POSIX 正则与 grep 的 -P 扩展（PCRE）](https://github.com/pcre2project/pcre2)
- [xxd 手册（-p 反向还原的用法）](https://man7.org/linux/man-pages/man1/hexdump.1.html)
- [Miller (mlr)：处理 CSV/TSV/JSON 的一行流工具](https://miller.readthedocs.io/en/latest/)
