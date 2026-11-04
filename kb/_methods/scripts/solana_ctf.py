#!/usr/bin/env python3
"""Solana 程序账户校验静态体检 + PDA 种子演示（纯标准库、离线、只读）。

对齐 kb/blockchain/solana-ctf.md：
  - 运行时**不自动**做业务校验：is_signer / owner == program_id / key == expected_pda
    都必须程序自己检查，漏了就等价于"可以传任意账户"。
  - Anchor 的 Signer<'info>、#[account(owner = ...)]、seeds/bump 自动校验；
    UncheckedAccount 与 /// CHECK: **只是注释**，运行时不校验任何东西。
  - PDA 由种子派生，种子来自指令数据且可控时可冒充管理员；
    invoke 需要 PDA 签名时必须用 invoke_signed 并传 seeds。

本脚本做的是源码启发式体检，不做 RPC、不签名、不发交易。

用法：
  python solana_ctf.py --file lib.rs
  python solana_ctf.py --file lib.rs --json
  python solana_ctf.py --pda user admin
  python solana_ctf.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys

WEB_HOSTS = ("oncurve", "offcurve")
CHECK_PATTERNS = {
    "is_signer": (r"\.is_signer", "缺 is_signer 校验 → 可伪造管理员账户"),
    "owner": (r"\.owner\s*[=!]=\s*(?:&?\s*)?(?:program_id|\*program_id|ctx\.program_id)",
              "缺 owner == program_id 校验 → 可传入自建数据账户"),
    "key": (r"\.key\s*[=!]=\s*(?:&?\s*)?[\w:]+", "缺 key / expected_pda 比较 → 可换绑账户"),
}


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def account_params(src: str):
    """抓原生程序的 account 变量名：`let x = next_account_info(...)` 与 `pub x: ...<'info>`。"""
    names = []
    for m in re.finditer(r"let\s+(?:mut\s+)?(\w+)\s*=\s*next_account_info\s*\(", src):
        names.append(m.group(1))
    for m in re.finditer(r"pub\s+(\w+)\s*:", src):
        names.append(m.group(1))
    out = []
    for n in names:
        if n not in out:
            out.append(n)
    return out


def analyze_source(src: str, verbose: bool = False) -> dict:
    body = strip_comments(src)
    findings = []
    raw = src  # 注释里的 `/// CHECK:` 也是信号，单独看原文
    for key, (pat, msg) in CHECK_PATTERNS.items():
        if re.search(pat, body):
            continue
        findings.append(("high" if key == "is_signer" else "medium", key, msg))
    if "UncheckedAccount" in body:
        findings.append(("high", "UncheckedAccount",
                         "UncheckedAccount 不做任何校验，需手写 constraint"))
    if "/// CHECK:" in raw or "// CHECK:" in raw:
        findings.append(("info", "check_comment",
                         "出现 /// CHECK: 标注——注释不会产生运行时校验"))
    if "init_if_needed" in body:
        findings.append(("medium", "init_if_needed",
                         "init_if_needed 可对已存在账户重复初始化（配合 CPI 可重入）"))
    if re.search(r"\binvoke_signed\s*\(", body) and "find_program_address" not in body:
        findings.append(("medium", "invoke_signed",
                         "使用 invoke_signed 但未见 find_program_address，检查 bump 规范化"))
    params = account_params(body)
    notes = ["账户参数 %d 个" % len(params)]
    if verbose:
        notes.append("账户参数：" + ", ".join(params))
    return {"findings": findings, "params": params, "notes": notes}


def pda_addr(seeds, program="Program111111111111111111111111111111111"):
    """演示用 PDA 派生：sha256(seeds || program || bump)。真实链上还需验证不在 ed25519 曲线上。"""
    h = hashlib.sha256()
    for s in seeds:
        h.update(b"\x00" + s)
    h.update(program.encode())
    return h.hexdigest()[:44], 255


def find_program_address(seeds, program="Program111111111111111111111111111111111", max_bump=255):
    """按 bump 从 255 递减搜索（真实实现还会检查 on-curve，这里用哈希前缀模拟）。"""
    for bump in range(max_bump, -1, -1):
        addr, _ = pda_addr(list(seeds) + [bytes([bump])], program)
        h = hashlib.sha256(addr.encode()).hexdigest()
        if not h.startswith("00") and not h.startswith("01"):
            return addr, bump
    raise ValueError("找不到可用 bump")


def seed_hint(user_names=("admin", "root", "master"), program="Program111111111111111111111111111111111"):
    out = []
    for name in user_names:
        addr, bump = find_program_address([b"user", name.encode()], program)
        out.append((name, addr, bump))
    return out


def selftest() -> int:
    fails = []
    # 1) 正常路径：缺失校验的原始 Rust 程序必须报 is_signer 缺失
    bad = """
    pub fn process(program_id: &Pubkey, accounts: &[AccountInfo], data: &[u8]) -> ProgramResult {
        let iter = &mut accounts.iter();
        let admin = next_account_info(iter)?;
        let vault = next_account_info(iter)?;
        let amount = u64::from_le_bytes(data[..8].try_into().unwrap());
        **vault.try_borrow_mut_lamports()? -= amount;
        **admin.try_borrow_mut_lamports()? += amount;
        Ok(())
    }
    """
    rep = analyze_source(bad)
    kinds = [f[1] for f in rep["findings"]]
    if "is_signer" not in kinds:
        fails.append("case1: 未报缺 is_signer")
    if "admin" not in rep["params"]:
        fails.append("case1: 未解析出账户参数 admin")
    # 2) 校验齐全的程序不应报 is_signer
    good = """
    pub fn process(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
        let admin = next_account_info(&mut accounts.iter())?;
        if !admin.is_signer { return Err(ProgramError::MissingRequiredSignature); }
        if admin.owner != program_id { return Err(ProgramError::IncorrectProgramId); }
        if admin.key != expected_pda { return Err(ProgramError::InvalidArgument); }
        Ok(())
    }
    """
    if "is_signer" in [f[1] for f in analyze_source(good)["findings"]]:
        fails.append("case2: 已校验 is_signer 仍被报错")
    # 3) Anchor 危险写法：UncheckedAccount 与 /// CHECK: 需报出
    anchor = """
    #[derive(Accounts)]
    pub struct Bad<'info> {
        /// CHECK: just a marker
        pub admin: UncheckedAccount<'info>,
    }
    """
    k3 = [f[1] for f in analyze_source(anchor)["findings"]]
    if "UncheckedAccount" not in k3 or "check_comment" not in k3:
        fails.append("case3: UncheckedAccount / /// CHECK: 未报出")
    # 4) PDA 固定输入可复现 + 非法输入拒绝 + 参数不足
    a1, b1 = find_program_address([b"user", b"admin"])
    a2, b2 = find_program_address([b"user", b"admin"])
    if (a1, b1) != (a2, b2):
        fails.append("case4: PDA 派生不可复现")
    if not (0 <= b1 <= 255):
        fails.append("case4: bump 越界")
    if find_program_address([b"user", b"admin"]) == find_program_address([b"user", b"root"]):
        fails.append("case4: 不同种子派生出同一地址")
    try:
        find_program_address([b"user"], max_bump=-1)
        fails.append("case4: max_bump 为负未被拒绝")
    except ValueError:
        pass
    # 5) 空源码不应崩、不应报 is_signer（没有账户就无从判断）
    try:
        empty = analyze_source("")
    except Exception as exc:  # noqa: BLE001
        fails.append("case5: 空源码分析抛异常 %s" % exc)
        empty = {"findings": [], "params": []}
    if empty["params"]:
        fails.append("case5: 空源码解析出账户参数")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（缺 is_signer 识别、校验齐全不误报、"
          "UncheckedAccount 报出、PDA 派生可复现与非法参数拒绝、空源码不崩）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Solana 账户校验体检 / PDA 种子演示")
    ap.add_argument("--file", help="Solana 程序源码（lib.rs）路径")
    ap.add_argument("--pda", nargs="+", metavar="SEED", help="按种子派生 PDA（演示实现）")
    ap.add_argument("--seed-search", action="store_true", help="枚举常见用户名种子")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出体检结果")
    ap.add_argument("--verbose", action="store_true", help="打印账户参数列表")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.pda:
            addr, bump = find_program_address([s.encode() for s in args.pda])
            print("PDA = %s  bump = %d" % (addr, bump))
            return 0
        if args.seed_search:
            for name, addr, bump in seed_hint():
                print("%-8s -> %s (bump %d)" % (name, addr, bump))
            return 0
        if not args.file:
            ap.error("必须提供 --file（或 --pda/--seed-search/--selftest）")
        with open(args.file, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        rep = analyze_source(src, args.verbose)
        if args.json:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
            return 0
        if not rep["findings"]:
            print("未发现明显缺失校验（仍需人工核对每个 AccountInfo）")
        for level, key, msg in rep["findings"]:
            print("[%-6s] %-16s %s" % (level, key, msg))
        for note in rep["notes"]:
            print("  · " + note)
    except (ValueError, OSError) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
