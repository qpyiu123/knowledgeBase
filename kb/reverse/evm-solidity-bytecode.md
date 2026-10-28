---
title: Solidity / EVM 字节码反编译（合约反汇编与 storage 还原）
category: reverse
tags: [solidity, evm, 智能合约, decompile, storage]
signals: [附件是 .sol 源码或 0x60 开头的十六进制字节码, 题目给了一个合约地址与 RPC 节点, 有 Bytecode 字段且以 6080604052 开头, 提示「合约」「链」「以太坊」「部署」, 存在 keccak256 选择器分发器, 数据以 0x 加 3000+ 位十六进制出现, 题目要求调用合约某个函数拿 flag, 出现 JSON ABI 列表, 有 .bin 与 .abi 两个文件]
difficulty: hard
source: "evm.codes / Solidity 文档 / Dedaub"
tools: [python, ethers, foundry, evm]
updated: 2026-10-22
relates_to: [blockchain/evm-storage-slot.md]
---

## 一、识别信号（题面长什么样）

- 附件是 `Challenge.sol`、`challenge.bin`、`abi.json`，或题面给一个合约地址 + RPC。
- 十六进制数据以 `6080604052`（`PUSH1 0x80 PUSH1 0x40 MSTORE`，Solidity 固定前缀）开头。
- 题面提示：`合约`、`智能合约`、`EVM`、`以太坊`、`Solidity`、`bytecode`、`storage`。
- 有 `keccak256` 选择器分发：`PUSH4 xxxxxxxx` + `EQ` + `PUSH2 dst` + `JUMPI`。
- 题目要求"调用合约的 `solve()`"或"让 `isSolved()` 返回 true"。
- 出现 `0x` + 数千字符的十六进制，或 `bin/`、`.abi` 文件。
- 账户余额、`msg.sender`、`tx.origin` 相关逻辑 —— 常见考点。

## 二、原理

### 1. EVM 执行模型

- 栈式虚拟机，256 位大整数，`PUSH1..PUSH32` 压栈。
- 合约调用时，前 4 字节是**函数选择器** = `keccak256("func(uint256)")[:4]`。
- 编译器在每个 public 函数入口生成分发器：

```
PUSH1 0x00
CALLDATALOAD
PUSH1 0xe0
SHR              ← 取前 4 字节
DUP1
PUSH4 0x12345678
EQ
PUSH2 0x00aa
JUMPI
```

### 2. Storage Layout

- 状态变量按**槽位（slot）**顺序存放，每个 slot 32 字节。
- `bool`/`uint8` 等小类型会**打包**（packing）进同一个 slot。
- `mapping` 的值位置 = `keccak256(key . slot)`；`dynamic array` = `keccak256(slot)` 起始。
- 逆向时一旦识别出 `SSTORE`/`SLOAD` 的 slot 常量，就能还原变量名与结构。

### 3. 常见考点逻辑

| 考点 | 特征 |
|---|---|
| `tx.origin` 钓鱼 | `CALLER` vs `ORIGIN` 比较 |
| 整数溢出 | `ADD`/`MUL` 后无 `LT`/`GT` 检查（<0.8.0） |
| delegatecall 注入 | `DELEGATECALL` + 固定地址 |
| 自毁 | `SELFDESTRUCT` |
| 隐蔽布尔 | `isSolved` 用 slot 状态拼接 |

## 三、解题步骤

1. **反汇编**：`evm disasm <bytecode>` 或 `ethersplay` / `panoramix` / [evm.codes](https://www.evm.codes/) 在线。
2. **找分发器**：搜 `PUSH4`，把所有选择器列出来，反查函数名（`4byte.directory`）。
3. **定位 solve 函数**：题面名字（`solve`、`win`、`flag`）→ keccak256 算出选择器，在字节码里搜。
4. **还原 storage**：搜 `SSTORE`/`SLOAD`，记录 slot 号；`PUSH32` 常量里可能藏着 flag 校验值。
5. **写调用**：`cast call` / `ethers` / `web3.py`。
6. **本地起链验证**：`anvil` + `forge create`。

## 四、可直接运行的脚本

反汇编用 `evm`（foundry）：

```bash
# 安装：curl -L https://foundry.paradigm.xyz | bash && foundryup
evm disasm challenge.bin
```

计算函数选择器：

```python
from eth_utils import keccak

def selector(sig: str) -> str:
    return "0x" + keccak(text=sig)[:4].hex()

for s in ["solve()", "isSolved()", "win(uint256)", "getFlag()", "pwn()"]:
    print(s, selector(s))
```

在字节码里定位选择器：

```python
import re

hexdata = open("challenge.bin").read().strip().replace("\n", "")
sel = "63" + "1be2b8e6"        # PUSH4 0x1be2b8e6
idx = hexdata.find(sel)
print("found at nibble offset", idx)
print(hexdata[max(0, idx-200): idx+200])
```

storage 槽位扫描（需要 RPC）：

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://RPC.TARGET"))
ADDR = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

for slot in range(8):
    v = w3.eth.get_storage_at(ADDR, slot)
    if int.from_bytes(v, "big"):
        print("slot", slot, v.hex())
```

调用 solve：

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://RPC.TARGET"))
acct = w3.eth.accounts[0]
abi = open("challenge.abi").read()
c = w3.eth.contract(address=ADDR, abi=abi)

tx = c.functions.solve().build_transaction({
    "from": acct, "nonce": w3.eth.get_transaction_count(acct), "gas": 200000})
h = w3.eth.send_transaction(tx)
w3.eth.wait_for_transaction_receipt(h)
print("solved =", c.functions.isSolved().call())
```

用 foundry 本地复现：

```bash
anvil --fork-url http://RPC.TARGET &
forge create --rpc-url http://127.0.0.1:8545 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  src/Challenge.sol:Challenge
cast call $ADDR "isSolved()(bool)" --rpc-url http://127.0.0.1:8545
```

## 五、常见坑 / 变体

- **没有源码只有字节码**：先用 `panoramix`（Vyper 编译器写的反编译器）或 [dedaub](https://dedaub.com/) 的在线 decompiler 看伪代码。
- **Solidity 版本差异**：0.4.x 与 0.8.x 的 `revert` 逻辑不同，0.8 溢出检查会多出 `LT`/`SLT` + `revert`。
- **4byte.directory**：选择器反查函数名（不一定匹配你的语义）。
- **storage 里 mapping**：值在 `keccak256(abi.encode(key, slot))`，不能直接 `get_storage_at(slot)`。
- **`immutable` / `constant` 不占 slot** —— 值被直接编译进字节码，搜 `PUSH32` 更有效。
- **`ABI decoder` 坑**：`bytes`/`string` 需要动态偏移，手工调用时容易错。
- **变体：Yul / 内联汇编** —— 字节码更少，逻辑更隐晦，但常量更集中。
- **变体：EVM 字节码混淆（未编译的原始汇编）** —— 用 `evm.codes` 逐条看。
- **变体：多合约 + `CREATE2` 地址计算** —— 需要复现部署地址。
- **注意**：若题目在测试网，别忘了在链上跑——本地模拟 `msg.sender` 可能不符。

## 六、参考来源

- [evm.codes — EVM Opcode Playground](https://www.evm.codes/)
- [Crytic — evm-opcodes](https://github.com/crytic/evm-opcodes)
- [panoramix](https://github.com/eveem-org/panoramix)
- [ethersplay](https://github.com/crytic/ethersplay)
- [Solidity 官方文档 — Layout of State Variables in Storage](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html)
- [Dedaub EVM Decompiler](https://dedaub.com/product/decompiler/)
