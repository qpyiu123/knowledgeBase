---
title: "zkCTF 2024 WriteUp By ChaMd5"
category: misc
tags: ["zkCTF", "misc", "zk-SNARK", "circom", "groth16", "halo2_proofs"]
signals: ["zkCTF 2024", "zk-SNARK", "circom", "groth16", "halo2_proofs", "fibonacci-circuit", "div-circuit", "range-check", "misc_unknown", "zkCTF", "zkSNARK", "Rust", "gate", "CheckIn"]
difficulty: medium
source: "https://www.ctfiot.com/162396.html"
tools: ["Rust"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# zkCTF 2024 WriteUp By ChaMd5

> 赛事：zkCTF 2024 | 方向：misc | 难度：medium | 工具：Rust

## 一句话总结

zkCTF 2024 zkSNARK 系列，覆盖 circom groth16 入门到 halo2_proofs Rust 自定义 gate 高级用法。

## 攻击链

1. CheckIn 题：circom 写 .circom→r1cs/wasm/sym 编译→input.json witness.wtns→snarkjs groth16 prove 生成 proof.json+public.json/中高级题 halo2_proofs Rust 实现 FibonacciCircuit 配置 add gate + U8 range-check table + DivCircuit a/b/c/r/k 列 + mul+add 双 gate + assign_range + assign_witness + expose_public 三件套 / generate_keys 调 ParamsKZG::setup + keygen_vk/pk / generate_proof 调 create_proof 用 KZGCommitmentScheme+ProverGWC+Challenge255 transcript + 写出 proof/param/vk 三文件

## 关键 payload

```
circom checkin.circom --r1cs --wasm --sym -c  snarkjs groth16 prove ../CheckIn_groth16.zkey witness.wtns proof.json public.json
```

## 经验教训

circom 是 zkSNARK DSL 入门工具，halo2_proofs 是 Rust 实现 zk 电路的工业级库；range check 通过 (1..range).fold(expr * (value - a)) 实现；BN256 Pasta 域 + KZG commitment 是现代 zk 标准组合。

## 标签

zk-SNARK、circom、groth16、halo2_proofs、fibonacci-circuit、div-circuit、range-check

## 参考来源

- https://www.ctfiot.com/162396.html
- 原文件：zkCTF_2024_WriteUp_By_ChaMd5.full.md
