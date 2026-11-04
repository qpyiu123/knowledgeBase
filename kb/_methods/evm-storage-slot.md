---
title: 方法卡 · EVM storage 槽位读取与还原
category: blockchain
tags: [evm, 存储槽, keccak256, mapping, private 变量, ctf]
signals:
  - "题目说 flag 藏在合约的 private 变量里"
  - "isSolved() 直接比较某个 storage 变量"
  - "read_slot 或 assembly sstore 可任意写"
  - "变量顺序和打包影响 slot 编号，需要手算布局"
  - "web3.eth.getStorageAt 能读出非零槽值"
  - "mapping 或动态数组里存着关键数据"
difficulty: hard
source: kb/blockchain/evm-storage-slot.md
updated: 2026-11-03
tools: [python3, web3.py, cast, foundry]
---
## 适用场景

合约题里"数据在链上但看不见"是最常见的套路。EVM 每个合约有 2^256 个 32 字节槽，
`private` 只是编译期可见性，链上数据全部公开：`eth_getStorageAt(addr, slot)`
能读任意槽。关键是把"变量名"翻译成"槽号"，再把 32 字节槽值按布局拆回语义值。

## 前置条件

- 知道合约地址与源码（没有源码就用 `cast storage` 盲扫前 20 个槽看可打印段）。
- 需要 keccak256：`web3.py`/`eth_utils` 可用则直接用；离线环境用本卡脚本自带的
  Keccak-256 实现（注意是 Ethereum 的 Keccak，不是 NIST SHA3，padding 0x01 vs 0x06）。
- RPC 端点（本地 anvil 或题目给的 `http://TARGET:8545`）。

## 步骤

1. **算布局**：值类型按声明顺序从 slot 0 起排，小于 32 字节的从**低位**打包进同一槽
   （`address a; uint8 b;` → a 占 0~159 位、b 占第 160~167 位）；结构体与数组总起新槽。
2. **mapping**：声明槽 `p` 只占位，`m[k]` 在 `keccak256(abi.encode(k, p))`，
   地址键要左补 12 字节零凑满 32 字节，不是字符串拼接。
3. **动态数组**：声明槽 `p` 存长度，元素从 `keccak256(p)` 开始，每个元素占
   `ceil(size/32)` 个槽。
4. **string/bytes**：长度 ≤31 时数据同槽、最低字节存 `len*2`；>31 时主槽存
   `len*2+1`，数据在 `keccak256(p)`。
5. **读值**：`web3.eth.get_storage_at(addr, slot)` 或
   `cast storage CONTRACT SLOT --rpc-url ...`，十六进制转字节后按布局拆字段。
6. **需要写**：找任意写原语（数组越界、`assembly sstore(add(0, idx), v)`、
   `delegatecall`），把目标槽直接写成满足 `isSolved` 的值。

## 立即可用脚本

`kb/_methods/scripts/evm_storage_slot.py`（纯标准库，自带 Keccak-256，离线）

```
python evm_storage_slot.py --layout layout.json --dump slots.json
python evm_storage_slot.py --mapping 0xUser 3
python evm_storage_slot.py --array 2 --index 1 --elem-slots 1
python evm_storage_slot.py --string 0x666c61677b7838787d
python evm_storage_slot.py --selftest
```

参数：

- `--layout` + `--dump`：布局 JSON（`{"variables":[{"name","type","size"}]}`）与槽值 JSON
  （`{"0":"0x...","1":"0x..."}`），按布局拆字段并打印可打印 ASCII。
- `--mapping KEY SLOT`：算 mapping 元素槽；KEY 支持十进制/`0x` 数值与 `0x` 地址。
- `--array P --index N --elem-slots K`：算动态数组第 N 个元素的槽。
- `--string HEX` / `--string-bytes HEX`：把 32 字节槽值按 string 规则解码；
  长字符串会提示数据在 `keccak256(slot)`。
- `--selftest`：断言 keccak 已知向量、槽位公式、非法参数拒绝、布局打包解包。

失败行为：变量大小 >32、负索引、布局里没有该变量、长字符串缺数据、槽值不是 32 字节，
都在 stderr 打印 `失败：…` 返回 2；自检通过打印 `selftest ok: …` 返回 0。

## 手工示例

```
$ python evm_storage_slot.py --layout layout.json --dump slots.json
owner            address    slot=0   0xff               ....................
solved           bool       slot=0   0x0                .
secret           bytes32    slot=1   0x666c61677b7838787d .......................flag{x8x}
$ cast index address 0x00000000000000000000000000000000000000ff 3
0x763723c073cfbae27d251b45742e6578f7eb79e9310f394dd771a44fd8e2ec61
$ python evm_storage_slot.py --mapping 0x00000000000000000000000000000000000000ff 3
0x763723c073cfbae27d251b45742e6578f7eb79e9310f394dd771a44fd8e2ec61
```

## 失效场景

- `immutable`/`constant` 变量不在 storage，它们在字节码里，要读 bytecode 反推。
- 合约未部署或已 selfdestruct：`eth_getStorageAt` 全 0（EIP-6780 后销毁语义有变化）。
- 槽值被结构化压缩（struct 跨槽、继承导致基类变量先占槽）：必须按完整继承链重新算布局。
- 编译优化改变了打包顺序（罕见）或用了 transient storage (EIP-1153)：读 `tload` 语义不同。

## 相关文档

- `kb/blockchain/solidity-reentrancy.md`：写槽前的可利用原语（重入/未校验调用）。
- `kb/blockchain/solidity-integer-overflow.md`：余额门槛类 `isSolved` 的溢出打法。
- `kb/_methods/onchain_base64_decode.md`：槽里解出的 base64 继续解码。

## 目录与收录说明

- 卡片：`kb/_methods/evm-storage-slot.md`；脚本：`kb/_methods/scripts/evm_storage_slot.py`。
- 对应 backlog 项 `evm-storage-slot`（category=blockchain），源文档
  `kb/blockchain/evm-storage-slot.md`。
