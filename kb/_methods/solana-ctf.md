---
title: 方法卡 · Solana 程序账户校验体检
category: blockchain
tags: [solana, anchor, is_signer, pda, 账户校验, ctf]
signals:
  - "Solana 入口接收 AccountInfo 数组"
  - "只比较 admin.key，未查 is_signer"
  - "Anchor 使用 UncheckedAccount 或 CHECK 注释"
  - "transfer/assign 前没查账户 owner"
  - "PDA 种子来自指令数据且可控（如 user_name）"
  - "题面提示：你可以随便传账户、signer 未校验"
difficulty: hard
source: kb/blockchain/solana-ctf.md
updated: 2026-11-03
tools: [python3, rust, anchor, solana-cli, solders]
---
## 适用场景

Solana 方向的 CTF：题目给一个 Rust 原生程序或 Anchor 程序，漏洞几乎总是
"少了一行校验"。Solana 运行时**不自动**做业务层校验，程序必须自己检查
`is_signer`、`owner == program_id`、`key == expected_pda`；漏掉任意一条，
攻击者就能塞入任意账户把逻辑骗过去。

## 前置条件

- 程序源码 `lib.rs`（或反编译产物），能看到 `process_instruction` 的账户列表。
- 题目给的 program id、已知 PDA/vault 地址、能连的 RPC（本地 `solana-test-validator`
  或题目 RPC）。
- 客户端库：`solders` + `solana-py`（构造 `AccountMeta` 时能把 `is_signer=False`）。

## 步骤

1. **列账户**：把 `next_account_info` 的每个变量与它的校验列成表；
   Anchor 工程则看 `#[derive(Accounts)]` 结构体字段类型。
2. **找缺失项**：对照下表逐条勾。原生程序里的 `if !admin.is_signer { ... }`
   通常被出题人删掉了。

   | 校验 | 作用 | 漏了会怎样 |
   |---|---|---|
   | `account.is_signer` | 该账户是否签名 | 伪造任意"管理员"账户 |
   | `account.owner == program_id` | 数据归本程序所有 | 传入自建数据账户 |
   | `account.key == expected_pda` | 地址是否为预期 PDA | 换绑账户骗过逻辑 |
   | `has_one` / `constraint` | 关联校验 | 关联关系被绕过 |

3. **注意注释陷阱**：`UncheckedAccount` 与 `/// CHECK:` **只是注释**，Anchor
   不会做任何校验，必须手写 `constraint`。
4. **PDA 种子可控**：若 `find_program_address(&[b"user", user_name...])` 的
   `user_name` 来自指令数据，用 `admin`/`root` 等常见值枚举出管理员 PDA 冒充。
5. **构造交易**：`AccountMeta(pubkey=victim, is_signer=False, is_writable=True)`，
   只用自己的 keypair 签名即可触发。
6. **验证**：本地 validator 上先跑通，再打远程，最后触发题目 `solved` 判定。

## 立即可用脚本

`kb/_methods/scripts/solana_ctf.py`（纯标准库、离线、不连 RPC）

```
python solana_ctf.py --file lib.rs
python solana_ctf.py --file lib.rs --verbose
python solana_ctf.py --file lib.rs --json
python solana_ctf.py --pda user admin
python solana_ctf.py --seed-search
python solana_ctf.py --selftest
```

参数：

- `--file`：Solana 源码，做缺校验启发式体检（is_signer / owner / key /
  UncheckedAccount / /// CHECK: / init_if_needed / invoke_signed）。
- `--verbose`：额外打印解析到的账户参数名。
- `--json`：机器可读输出，便于喂给后续脚本。
- `--pda SEED...` / `--seed-search`：**演示用** PDA 派生与常见用户名种子枚举，
  真实链上地址仍需用 `solders` 的 `Pubkey.find_program_address` 复核。
- `--selftest`：断言缺 is_signer 能报出、校验齐全不误报、Anchor 危险写法能报出、
  PDA 派生可复现且非法 bump 被拒、空源码不崩。

失败行为：文件不存在或参数非法，stderr `失败：…` 返回 2；自检通过打印
`selftest ok: …` 返回 0。脚本只做静态提示，结论需人工核对每个账户。

## 手工示例

```
$ python solana_ctf.py --file lib.rs --verbose
[high  ] is_signer        缺 is_signer 校验 → 可伪造管理员账户
[medium] owner            缺 owner == program_id 校验 → 可传入自建数据账户
[medium] key              缺 key / expected_pda 比较 → 可换绑账户
  · 账户参数：admin, vault
$ python solana_ctf.py --seed-search
admin    -> c5d8e275e61e026e8a6a7208feb78e9dfc943bebd271 (bump 255)
```

## 失效场景

- Anchor 的 `Signer<'info>`、`#[account(owner = …)]` 已自动校验：脚本按关键字判断，
  可能出现误报或漏报，必须人工核对字段类型。
- 校验存在但对象不对（`Signer` 换绑、`has_one` 指向别的字段）：静态文本看不出来。
- 程序逻辑写成 CPI 中间人、重复账户攻击、`init_if_needed` 重入：需要动态验证。
- 缺 lamports 来源 / rent_exempt 检查：脚本完全不检查，需手工看余额流向。

## 相关文档

- `kb/blockchain/solana-ctf.md`：本文的主要来源，含原生 Rust 与 Anchor 例子。
- `kb/blockchain/solidity-reentrancy.md`：EVM 侧"缺少检查"的同类思路。
- `kb/_methods/solidity-reentrancy.md`：EVM 重入/溢出的脚本化体检。

## 目录与收录说明

- 卡片：`kb/_methods/solana-ctf.md`；脚本：`kb/_methods/scripts/solana_ctf.py`。
- 对应 backlog 项 `solana-ctf`（category=blockchain），源文档 `kb/blockchain/solana-ctf.md`。
