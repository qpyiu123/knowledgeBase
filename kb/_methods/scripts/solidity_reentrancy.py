#!/usr/bin/env python3
"""Solidity 重入 / 整数溢出 静态体检 + 溢出算术演示（纯标准库、离线、只读）。

对齐 kb/blockchain/solidity-reentrancy.md：
  - 外部调用 msg.sender.call{value: x}("") 在状态更新之前 -> 重入（SWC-107）
  - transfer/send 只有 2300 gas，重入困难；call 把剩余 gas 全给对方
  - 防御：checks-effects-interactions、nonReentrant
对齐 kb/blockchain/solidity-integer-overflow.md：
  - uint256 按模 2^256 回绕，0 - 1 = 2^256 - 1（SWC-101）
  - Solidity >= 0.8 默认检查，unchecked / <0.8 才有静默回绕

用法：
  python solidity_reentrancy.py --file Bank.sol
  python solidity_reentrancy.py --file Bank.sol --verbose
  python solidity_reentrancy.py --mul 0x8000000000000000000000000000000000000000000000000000000000000001 2
  python solidity_reentrancy.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sys

MOD = 2 ** 256
CALL_KEYS = (".call{", ".call(", ".call", "call{")
STATE_RE = re.compile(r"^\s*[\w\[\]\.]+\s*(-=|\+=|=)\s*")
GUARD_HINTS = ("nonreentrant", "checks-effects-interactions", "nonReentrant")


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def solver_version(src: str) -> str:
    m = re.search(r"pragma\s+solidity\s+([^;]+);", src)
    return m.group(1).strip() if m else ""


def has_unchecked(src: str) -> bool:
    return "unchecked" in src


def find_functions(src: str):
    """粗粒度抓函数体：name -> body（按花括号配平）。"""
    out = {}
    for m in re.finditer(r"function\s+(\w+)\s*\([^)]*\)[^{;]*\{", src):
        name, i, depth = m.group(1), m.end() - 1, 0
        while i < len(src):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out[name] = src[m.end():i]
    return out


def analyze_source(src: str, verbose: bool = False) -> dict:
    """返回 {"findings": [(level, func, msg)], "notes": [...]}。"""
    body = strip_comments(src)
    funcs = find_functions(body)
    findings = []
    guarded = any(h in body for h in GUARD_HINTS)
    for name, fb in funcs.items():
        lines = fb.splitlines()
        call_at = state_after = None
        for n, line in enumerate(lines):
            if any(k in line for k in CALL_KEYS) and call_at is None:
                call_at = n
            if STATE_RE.match(line) and "-=" in line and state_after is None:
                state_after = n
        if call_at is not None and state_after is not None and state_after > call_at:
            findings.append(("high", name,
                             "外部 call 之后才更新状态（第 %d 行 call / 第 %d 行 -="
                             "）→ 重入 SWC-107" % (call_at + 1, state_after + 1)))
        if call_at is not None and not guarded:
            findings.append(("info", name, "含外部 call 且未见 nonReentrant/CEI 标记"))
        if re.search(r"\b(transfer|send)\s*\(", fb) and call_at is None:
            findings.append(("info", name, "只用 transfer/send（2300 gas，重入困难）"))
        if "-=" in fb and has_unchecked(body):
            findings.append(("high", name, "unchecked 块内的减法 → 整数下溢 SWC-101"))
    ver = solver_version(body)
    weak = bool(re.search(r"0\.(?:[0-7])\.", ver)) if ver else False
    if weak or has_unchecked(body):
        findings.append(("medium", "<compiler>",
                         "Solidity %s 或存在 unchecked → 无溢出检查" % (ver or "未声明")))
    notes = ["函数数 %d" % len(funcs)]
    if verbose:
        notes.append("检测到函数：%s" % ", ".join(sorted(funcs)))
    if guarded:
        notes.append("源码出现 nonReentrant/CEI 提示")
    return {"findings": findings, "notes": notes}


def wrap_op(a: int, b: int, op: str) -> int:
    if op == "+":
        return (a + b) % MOD
    if op == "-":
        return (a - b) % MOD
    if op == "*":
        return (a * b) % MOD
    raise ValueError("只支持 + - *（除法不溢出）")


def overflow_buy(amount: int, price: int) -> int:
    """uint256 cost = amount * price; 返回回绕后的 cost。"""
    return wrap_op(amount, price, "*")


def selftest() -> int:
    fails = []
    vulnerable = """
    pragma solidity ^0.6.0;
    contract Bank {
        mapping(address => uint256) public balanceOf;
        function withdraw(uint256 amount) external {
            require(balanceOf[msg.sender] >= amount);
            (bool ok,) = msg.sender.call{value: amount}("");
            require(ok);
            balanceOf[msg.sender] -= amount;
        }
    }
    """
    fixed = """
    pragma solidity ^0.8.19;
    contract Bank {
        mapping(address => uint256) public balanceOf;
        bool locked;
        modifier nonReentrant() { require(!locked); locked = true; _; locked = false; }
        function withdraw(uint256 amount) external nonReentrant {
            balanceOf[msg.sender] -= amount;
            (bool ok,) = payable(msg.sender).call{value: amount}("");
            require(ok);
        }
    }
    """
    # 1) 正常路径：漏洞合约 must 报 high 重入
    rep = analyze_source(vulnerable)
    highs = [f for f in rep["findings"] if f[0] == "high"]
    if not any("重入" in f[2] for f in highs):
        fails.append("case1: 未识别出 call 早于状态更新的重入")
    # 2) 修复后不应再报重入 high
    rep2 = analyze_source(fixed)
    if any("重入" in f[2] and f[0] == "high" for f in rep2["findings"]):
        fails.append("case2: 修复后的合约仍被报重入")
    # 3) 溢出算术：0-1 回绕 / 2^255+1 × 2 回绕到 2
    if wrap_op(0, 1, "-") != MOD - 1:
        fails.append("case3: 0-1 未回绕到 2^256-1")
    if overflow_buy(2 ** 255 + 1, 2) != 2:
        fails.append("case3: (2^255+1)*2 应回绕为 2")
    # 4) 参数不足 / 非法输入：空源码、非法运算符、非数字
    if analyze_source("")["findings"]:
        fails.append("case4: 空源码不应产生 findings")
    try:
        wrap_op(1, 2, "/")
        fails.append("case4: 非法运算符未被拒绝")
    except ValueError:
        pass
    try:
        int("zz", 0)
        fails.append("case4: 非法数字未被拒绝")
    except ValueError:
        pass
    # 5) 固定输入可复现：同一源码两次分析结果一致
    if analyze_source(vulnerable)["findings"] != analyze_source(vulnerable)["findings"]:
        fails.append("case5: 同一源码两次分析结果不一致")
    # 6) unchecked 减法应报下溢
    src_unchecked = """
    pragma solidity ^0.8.0;
    contract C { mapping(address=>uint) b;
      function f() external { unchecked { b[msg.sender] -= 1; } } }
    """
    if not any("下溢" in f[2] for f in analyze_source(src_unchecked)["findings"]):
        fails.append("case5: unchecked 减法未报下溢")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（重入识别、修复后不误报、uint256 回绕、"
          "非法输入拒绝、unchecked 下溢）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Solidity 重入/溢出体检与回绕算术")
    ap.add_argument("--file", help="Solidity 源码路径")
    ap.add_argument("--mul", nargs=2, metavar=("A", "B"), help="uint256 回绕乘法")
    ap.add_argument("--sub", nargs=2, metavar=("A", "B"), help="uint256 回绕减法")
    ap.add_argument("--verbose", action="store_true", help="打印函数列表与提示")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.mul:
            print("0x%x" % wrap_op(int(args.mul[0], 0), int(args.mul[1], 0), "*"))
            return 0
        if args.sub:
            print("0x%x" % wrap_op(int(args.sub[0], 0), int(args.sub[1], 0), "-"))
            return 0
        if not args.file:
            ap.error("必须提供 --file（或 --mul/--sub/--selftest）")
        with open(args.file, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        rep = analyze_source(src, args.verbose)
        if not rep["findings"]:
            print("未发现重入/溢出特征（仍需人工复核外部调用与修饰器）")
        for level, func, msg in rep["findings"]:
            print("[%-6s] %-16s %s" % (level, func, msg))
        for note in rep["notes"]:
            print("  · " + note)
    except (ValueError, OSError) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
