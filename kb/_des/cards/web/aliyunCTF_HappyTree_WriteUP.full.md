---
title: "aliyunCTF HappyTree WriteUP"
category: web
tags: ["aliyunCTF HappyTree", "web", "merkle_tree_verify", "solidity_smart_contract", "keccak256_abi_encodePacked", "leaf_used_replay"]
signals: ["aliyunCTF HappyTree 2024", "merkle_tree_verify", "solidity_smart_contract", "keccak256_abi_encodePacked", "leaf_used_replay", "merkle_proof_construction", "ethereum_blockchain", "function_b_verify", "leaf_used_mapping", "blockchain", "aliyunCTF", "HappyTree", "WriteUP", "Solidity"]
difficulty: hard
source: "https://www.ctfiot.com/112421.html"
tools: ["Solidity"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# aliyunCTF HappyTree WriteUP

> 赛事：aliyunCTF HappyTree 2024 | 方向：web | 难度：hard | 工具：Solidity

## 一句话总结

aliyunCTF HappyTree WriteUP：Solidity Merkle Tree 验证合约 b(leafs, proofs, indexs) 接收 3 个 leaf + 4 个 proof + 4 个 index，verify 通过 keccak256(abi.encodePacked(hash, proof)) 计算路径验证 == root。

## 攻击链

1. Solidity Greeter 合约 + b(leafs[], proofs[], indexs[]) 函数 + verify(proof, leaf, index) Merkle 路径验证 (index%2==0 则 hash=keccak256(hash,proof) 否则 keccak256(proof,hash)) + used_leafs[leaf] 防止重放 + this.a(i, y) 调用 → 3 个 leaf (0x8137...cd6a, 0x28ca...79b6, 0x804c...31d) + 4 个 proofs + 4 个 indexs (0,1,2,4) + root 0x9b1a0a45cfdc60f45820808958c1895d44da61c8f804f5560020a373b23ad51e

## 关键 payload

```
leafs = [0x81376b..., 0x28cac3..., 0x804cd8..., 0x9b1a0a45cfdc60f45820808958c1895d44da61c8f804f5560020a373b23ad51e] / proofs[i] for i in 4 / indexs = [0,1,2,4] / verify(proofs, leaf, index) keccak256 abi.encodePacked
```

## 经验教训

Merkle Tree 在 CTF 区块链题中是验证批量 leaf 的标准结构；keccak256(abi.encodePacked(hash, proof)) 是按 index 奇偶交换参数的 Merkle 验证算法。

## 标签

merkle_tree_verify、solidity_smart_contract、keccak256_abi_encodePacked、leaf_used_replay、merkle_proof_construction、ethereum_blockchain、function_b_verify、leaf_used_mapping、blockchain_ctf

## 参考来源

- https://www.ctfiot.com/112421.html
- 原文件：aliyunCTF_HappyTree_WriteUP.full.md
