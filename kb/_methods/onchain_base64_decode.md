---
title: 方法卡 · 链上数据解码（合约 storage/calldata 里的 base64）
category: blockchain
tags: [方法卡, 区块链, evm, base64, hex, storage, calldata, 解码]
signals: [链上合约, storage 槽位是长 hex, 交易 calldata 很长, 地址里带数据, 部署交易带附加数据, setFlag 类合约]
difficulty: medium
source: kb/blockchain/evm-storage-slot.md
tools: [python, 内置脚本, cast, ethers]
updated: 2026-11-02
---

# 方法卡 · 链上数据解码（合约 storage/calldata 里的 base64）

## 适用场景

区块链题给出了 RPC 地址与合约地址（或部署交易 hash），flag 不在合约源码里，
而是藏在 **storage 槽位、构造函数参数、calldata、事件 log 的 data 字段**中，
且这些字段里常见"一长串 hex"或"hex 里再套 base64"。

## 前置条件

- 有可用的 RPC（本地 anvil/hardhat 或题目给的公链节点）。
- 已知合约地址（或部署交易的 input）。
- 理解基本布局：EVM 每槽 32 字节；`string`/`bytes` 是"长度 + 数据块"的长格式，
  `bytes32` 则直接大端存放。

## 步骤

1. 先拿源码/ABI：`cast code <addr>` 反汇编或 `cast abi-decode` 看构造参数。
2. 逐个读 storage：`cast storage <addr> <slot> --rpc-url <url>`，从 0 开始；长格式数据在
   `slot` 存长度、`slot + keccak256(slot)` 存内容。
3. 部署交易：`cast tx <hash>` 的 `input` 尾部就是构造参数，去掉 4 字节选择器后按 ABI 切分。
4. **把字段当 hex 解一次**：`bytes.fromhex(...)` → 可打印则直接出 flag；
   若是 base64 文本 → 用本卡脚本再解一层；若 base64 解出来是二进制 → 看 `final_head_hex` 判断是否压缩/图片。
5. 事件 log：`cast logs --address <addr>` 的 `data` 同样按上述流程处理。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/enc_chain_decode.py`

```powershell
# 自检（9 项：单层 base64 / 两层 hex→base64 / url / %xx / \x / rot13 / 不误判 / 深度上限 / 直命中）
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --selftest

# 链上字段：把 cast 输出去掉 0x、去掉右侧补零后喂进去（hex 自动解，里面若是 base64 再解一层）
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --data "5a6d78685a337476626d4e6f59576c75583249324e48303d" --json

# 链上字段在文件里（一行一个字段，已去 0x）
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --file work/q3/_chain_fields.txt --stop "" --json
```

- 公开函数：`decode_chain(text, max_depth=8, stop="flag{", allow_rot13=False)`；
  `detect_layer(text)` → `(name, bytes)`。
- ⚠️ **先去掉 `0x` 前缀和右侧 ABI 补零**：脚本只认纯 hex 字符，`0x...` 会被当作"原样文本"
  （`depth: 0, steps: []`），补零会破坏 base64 的 `=` 对齐。
- 输出里 `steps[i].encoding` 会告诉你"这一层是 hex 还是 base64"，
  `binary: true` 时只给 `hex_head`——说明解出来的不是文本，去查文件头。
- 自检输出形如 `selftest ok: 9/9（单层 base64、两层 hex→base64、url 解码、%xx 二字节 url、\x 转义、rot13 显式开启、默认不误判英文、深度上限、原文直接命中）`。

## 手工示例

链上常见形态：storage 里读到
`0x5a6d78685a337476626d4e6f59576c75583249324e48303d`（32 字节槽，右侧补 `00`）。

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --data "5a6d78685a337476626d4e6f59576c75583249324e48303d" --json
# steps: hex    -> "ZmxhZ3tvbmNoYWluX2I2NH0="
#        base64 -> "flag{onchain_b64}"
# => final: "flag{onchain_b64}", stop_hit: "flag{", depth: 2
```

即：链上给的是 **base64 的 hex 编码**，去掉 `0x` 与补零后脚本两层解完。

对比一个**二进制**结果：`--data "Q1RG//4gfw=="` 输出 `binary: true, hex_head: "435446fffe207f"`，
`final` 保持原串——脚本不会把二进制当文本吞掉，这正是我们要的行为。

## 失效场景

- **数据被压缩后再上链**（base64 → gzip）：本卡只解编码，解出 `1f 8b` 头就转 `decompress_chain.py`。
- **合约把数据做了异或/加密**：需要先读源码拿到密钥，不是纯编码问题。
- **storage 用了 mapping/动态数组**：槽位由 `keccak256(key . slot)` 决定，需要先算出真实槽位（见 `kb/blockchain/evm-storage-slot.md`）。
- **RPC 不可用/合约未部署**：只能从部署交易 input 里挖，别指望 `cast storage`。
- **超长 calldata**：注意 `0x` 前缀与 ABI 对齐补零，去掉右侧填充零再解，否则 base64 会被破坏。

## 相关文档

- `kb/blockchain/evm-storage-slot.md`（storage 布局、mapping 槽计算、读取命令）
- `kb/blockchain/solidity-access-control.md`（`setFlag` 权限题的横向思路）
- `kb/misc/encoding-chain.md`（编码层级识别顺序）
- `kb/_imported_cats/misc/NewStar CTF 2024 _ ezblockchain__official-316e4235a17371288d885a.md`（同类链上题原文）
- 方法卡：`kb/_methods/enc_chain_decode.md`、`kb/_methods/decompress_chain.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
