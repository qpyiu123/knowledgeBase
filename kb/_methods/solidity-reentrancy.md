---
title: 方法卡 · Solidity 重入与整数溢出
category: blockchain
tags: [solidity, 重入, swc-107, 整数溢出, swc-101, ctf]
signals:
  - "withdraw 外部 call 在扣余额之前"
  - "题面说合约里有 10 ETH、你只有 1 ETH，要掏空"
  - "判定目标为合约余额清零或玩家余额激增"
  - "合约用 call 而不是 transfer/send 转账"
  - "源码 pragma 是 0.7 以下，或出现 unchecked 块"
  - "uint256 cost = amount * price 这种乘法没做上限检查"
difficulty: hard
source: kb/blockchain/solidity-reentrancy.md, kb/blockchain/solidity-integer-overflow.md
updated: 2026-11-03
tools: [python3, solidity, foundry, web3.py, slither]
---
## 适用场景

两类最经典的智能合约题：**重入**（外部调用发生在状态更新之前，攻击合约在
`fallback` 里反复调用 withdraw）和**整数溢出**（uint256 按模 2^256 回绕，
`amount * price` 溢出成 0 或小值）。两者都以 `isSolved` 里"余额/状态变量满足条件"收尾。

## 前置条件

- 合约源码或字节码；有源码时直接用本卡脚本体检，无源码时在 `cast disassemble` 里找
  `CALL` 指令与 `SSTORE` 的相对顺序。
- 一个攻击合约模板（本卡给出 Foundry 与 web3.py 两种）。
- 本地 anvil/forge 环境，或题目给的 RPC。

## 步骤

1. **看重入三要素**：`withdraw` 里有 `msg.sender.call{value: x}("")`、
   状态更新 `balanceOf[msg.sender] -= amount` 写在这行**之后**、接收方是合约
   （有 `receive`/`fallback` 或 ERC777/ERC721 回调）。
2. **确认可重入性**：`transfer`/`send` 只有 2300 gas，不够重入；`call` 把剩余 gas
   全部交出，才能再次进函数。
3. **写攻击合约**：`attack()` 里 deposit 再 withdraw；`receive()` 里用计数器
   `count < N` 限制递归次数，避免 gas 耗尽。
4. **溢出路径**：找 `a * b`、`a - b` 这类未检查运算。工具函数里
   `uint256 cost = amount * price`，令 `amount = 2^255 + 1, price = 2` 得到 `cost = 2`
   （高位溢出被丢弃），于是能以 2 wei 买入巨量 token。
5. **版本与修饰器**：Solidity 0.8+ 默认检查溢出，只有 `unchecked` 块才有静默回绕；
   重入防护看 `nonReentrant` 与 checks-effects-interactions 顺序。
6. **本地跑通再做远程**：`forge test -vvv` 断言 `address(bank).balance == 0`。

## 立即可用脚本

`kb/_methods/scripts/solidity_reentrancy.py`（纯标准库、离线、只读）

```
python solidity_reentrancy.py --file Bank.sol
python solidity_reentrancy.py --file Bank.sol --verbose
python solidity_reentrancy.py --mul 0x8000000000000000000000000000000000000000000000000000000000000001 2
python solidity_reentrancy.py --sub 0 1
python solidity_reentrancy.py --selftest
```

参数：

- `--file`：Solidity 源码，按函数体做粗粒度顺序检查（call 与 `-=` 的先后）。
- `--verbose`：额外列出检测到的函数名与修饰器提示。
- `--mul A B` / `--sub A B`：演示 uint256 回绕（结果按 16 进制输出）。
- `--selftest`：断言重入识别、修复后不误报、`0-1` 与 `(2^255+1)*2` 回绕、非法输入拒绝。

失败行为：文件不存在、数字非法、运算符非法，stderr 打印 `失败：…` 返回 2；
自检通过打印 `selftest ok: …` 返回 0。静态检查是启发式，结论需人工复核。

## 手工示例

```
$ python solidity_reentrancy.py --file Bank.sol
[high  ] withdraw         外部 call 之后才更新状态（第 3 行 call / 第 5 行 -=）→ 重入 SWC-107
[medium] <compiler>       Solidity ^0.6.0 或存在 unchecked → 无溢出检查
$ python solidity_reentrancy.py --mul 0x8000000000000000000000000000000000000000000000000000000000000001 2
0x2
$ python solidity_reentrancy.py --sub 0 1
0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
```

## 失效场景

- 重入已用 `nonReentrant` 或先扣款（CEI）修复：本脚本仍可能给 info 级提示，需人工判断。
- 只读重入（read-only reentrancy）：外部调用期间读别的合约价格，脚本看不到跨合约语义。
- 字节码层面优化后原顺序不可见：需要反汇编（`cast disassemble`）逐条看 CALL/SSTORE。
- 溢出被 Solidity 0.8 的检查拦截：除非进 `unchecked`，否则乘法会 revert 而不是回绕。

## 相关文档

- `kb/blockchain/evm-storage-slot.md`：重入/溢出后把状态槽直接写成目标值。
- `kb/blockchain/solana-ctf.md`：非 EVM 链的同类"缺校验"思路对照。
- `kb/_methods/evm-storage-slot.md`：脚本化的槽位读取。

## 目录与收录说明

- 卡片：`kb/_methods/solidity-reentrancy.md`；脚本：
  `kb/_methods/scripts/solidity_reentrancy.py`。
- 对应 backlog 项 `solidity-reentrancy`（category=blockchain），源文档
  `kb/blockchain/solidity-reentrancy.md` 与 `kb/blockchain/solidity-integer-overflow.md`。
