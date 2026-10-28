---
title: AI 编码题打法（模型辅助逆向与找 bug 的实战流程）
category: ai
tags: [ai-coding, llm4decompile, reverse-assist, copilot, code-review]
signals: [题目给了大量混淆后的代码要求快速读懂, 题目要求在有限时间内找到二进制里的漏洞点, 附件是一个巨大的二进制或者源码树, 提示说可以用 AI 辅助分析, 题目要求写一个能跑通的 exp 或者脚本, 需要把汇编翻译成 C 再分析]
difficulty: medium
source: "LLM4Decompile 论文与数据集 / r2ai 文档 / 公开的 AI 辅助逆向实践"
tools: [python, ghidra, ida, llm4decompile, r2ai, gpt, claude, aider]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 给了几千行的反编译伪代码，人工读要几小时。
- 题目是"限时抢分"，需要快速定位逻辑。
- 二进制里函数极多，找不到入口。
- 需要把汇编/伪代码转成可编译的 C 再跑测试。
- 题目要求提交脚本而不是 flag。
- 提示里出现 "AI""copilot""用模型辅助"。

## 二、原理

**LLM 在逆向/找 bug 上的能力边界：**

| 任务 | 模型擅长 | 模型不擅长 |
| --- | --- | --- |
| 读伪代码、总结函数作用 | ✅ 强 | 精确的寄存器/栈偏移 |
| 把汇编翻译成 C | ✅ 中（LLM4Decompile 专门做） | 复杂控制流与结构体还原 |
| 识别已知算法（TEA/AES/RC4） | ✅ 强（靠常量特征） | 自定义加密 |
| 找缓冲区溢出/整数溢出 | ✅ 中（需给上下文） | 跨函数数据流跟踪 |
| 写 exp / 脚本 | ✅ 强 | 依赖版本的具体偏移 |

**核心方法论：把"大问题"切成"模型能一次吃下的片段"**，再人工串起来验证。**永远不要相信模型给出的地址/偏移/常量，必须回二进制验证。**

## 三、操作步骤

1. **建立函数地图**：先 `rabin2 -i`/Ghidra 导出函数列表，按大小与调用次数排序。
2. **喂接口而不喂全量**：每次给一个函数（或 200 行以内）的伪代码 + 它的调用者摘要。
3. **让模型做具体任务**：不要问"这是干嘛的"，改问"列出这个函数读写的全局变量""这个循环的终止条件是什么"。
4. **交叉验证**：模型给出的"算法名"用常量表核验（AES S-box、MD5 常量）。
5. **写成可执行物**：让模型输出"可编译的 C 复现"，用已知输入输出对比原始程序。
6. **找 bug**：给模型"函数 + 调用点 + 输入来源"，要求逐条列出可能的危险操作。

## 四、命令 / 脚本

```bash
# 1) 导出伪代码（Ghidra 无头模式）
analyzeHeadless /tmp/ghidra_proj proj -import ./target.bin \
  -postScript DecompileAll.py -scriptPath ./scripts -deleteProject
# 2) 生成函数摘要清单
rabin2 -s target | sort -k3 -n | tail -30
rabin2 -i target                      # 导入表
# 3) LLM4Decompile（把 x86 汇编反编译成 C）
pip install llm4decompile
llm4decompile-decompile --model LLM4Decompile-6.7b-v1.5 --file func.asm -o func.c
```

```python
#!/usr/bin/env python3
# 把函数切片喂给模型：控制上下文长度 + 强制结构化输出
import json, textwrap, re

MAX_LINES = 200

def slice_function(pseudo_c: str) -> str:
    lines = pseudo_c.splitlines()
    if len(lines) <= MAX_LINES:
        return pseudo_c
    head = lines[:40]
    tail = lines[-20:]
    return '\n'.join(head) + '\n  /* ... 省略 %d 行 ... */\n' % (len(lines) - 60) + '\n'.join(tail)

PROMPT = """你是一个逆向工程师。下面是 Ghidra 反编译出的一个函数。
请只输出 JSON，字段：
- purpose: 这个函数做什么（一句话）
- crypto_hint: 是否疑似加密/哈希，若是给算法名与依据（常量/循环结构）
- inputs: 外部可控的输入变量列表
- dangerous: 可能的内存/整数风险（给出具体行内容）
- unknowns: 你不确定的点
伪代码：
```c
{code}
```"""

def ask(llm, code):
    return llm(PROMPT.replace('{code}', slice_function(code)))

def merge(docs):
    """把多个函数的分析结果汇总成表"""
    for d in docs:
        j = json.loads(d)
        print('%-30s %s' % (j.get('purpose', '')[:30], j.get('crypto_hint')))
```

```python
#!/usr/bin/env python3
# 用常量表识别"模型说的算法对不对"（交叉验证）
import re

SIGNATURES = {
    'AES': ['63 7c 77 7b f2 6b 6f c5', 'c66363a5', '0x1b', 'sbox'],
    'MD5': ['d76aa478', 'e8c7b756', '242070db', '0x67452301'],
    'RC4': ['0x100, 0x100', 'prga', '0x100 bytes'],
    'TEA': ['0x9e3779b9', '2654435769'],
    'Base64': ['ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef'],
    'XXTEA': ['0x9e3779b9', 'delta'],
}

def verify(hint: str, binary_strings: str):
    table = SIGNATURES.get(hint.upper())
    if not table:
        return 'no reference'
    hits = [t for t in table if t.lower() in binary_strings.lower()]
    return '✓ 常量命中 %s' % hits if hits else '✗ 未找到常量，模型可能猜错'
```

```bash
# r2ai：把模型接到 radare2 里，对当前函数直接提问
r2 -qc 'aaa' target.bin
# (r2 内)
# > r2ai -d              ; 解释当前函数
# > r2ai -d ...          ; 追问
# > decai                ; 反编译视图
```

## 五、常见坑 / 变体

- **模型幻觉地址**：它给的 `0x4012ab` 很可能不存在，所有偏移必须回 IDA/Ghidra 核对。
- **上下文截断**：长函数被截断后模型会"编造"后半段，必须显式标注省略。
- **模型说"这是 AES"但实际是魔改**：看 S-box 是否被置换、轮数是否不同。
- **找 bug 要给数据流**：只给函数体，模型常把"不可达的检查"当有效；要给调用点与输入来源。
- **写 exp 时要给环境**：libc 版本、偏移、保护机制，模型不知道这些。
- **合规**：CTF 平台允许用 AI 就用；不允许时只用于"读伪代码"这类辅助，不直接提交生成的 flag。
- **变体**：LLM4Decompile 的多尺寸模型（1.3B/6.7B/33B）、用模型生成 YARA 规则、用模型批量写 byteman/injection 脚本。

## 六、参考来源

- [LLM4Decompile：用大模型反编译二进制代码（论文与数据集）](https://arxiv.org/html/2403.05286v3)
- [r2ai：radare2 的 LLM 集成（官方手册）](https://book.rada.re/plugins/r2ai.html)
- [Ghidra 官方文档（无头模式与脚本）](https://ghidra.re/)
- [radare2 官方手册（rabin2 用法）](https://book.rada.re/)
- [Aider：终端里的 AI 结对编程工具](https://aider.chat/)
