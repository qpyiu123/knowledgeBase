---
title: "量子安全 quantum ctf Qlotto Hack the box"
category: crypto
tags: ["Quantum CTF / Hack The Box QLotto", "crypto", "qiskit", "quantum-circuit", "Aer-simulator", "qasm-simulator"]
signals: ["Quantum CTF / Hack The Box QLotto 2025", "qiskit", "quantum-circuit", "Aer-simulator", "qasm-simulator", "QuantumCircuit", "H-S-T-Z-gates", "RXX-RYY-RZZ", "binomialtest", "misc_math", "Qlotto", "CTF", "Hack", "box"]
difficulty: hard
source: "https://www.ctfiot.com/297316.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 量子安全 quantum ctf Qlotto Hack the box

> 赛事：Quantum CTF / Hack The Box QLotto 2025 | 方向：crypto | 难度：hard

## 一句话总结

量子安全Qlotto CTF(Hack the box)量子电路+模拟器+6位bit映射+42取模,需理解Lotto/Test bit按位取反关系,用量子电路让test和lotto不同但guess==lotto得flag。

## 攻击链

1. 代码分析:server.py使用qiskit+QuantumCircuit(2qubit)+Aer qasm_simulator后端
2. generate_circuit(instructions):解析指令字符串"gate:params;..."格式
3. 1-qubit gates:H(h)+S(s)+T(t)+Z(z)
4. 2-qubit gates:RXX/RYY/RZZ(2 params:phase+qubits)+CX/CZ
5. validate_entropy:测0比特位100000 shots+binomtest+two-sided pvalue<0.01拒绝
6. extract_numbers:从memory中按6位一组(2bit lottery+4bit testing)
7. lotto_number = int(bits, 2) % 42 + 1
8. testing_number = int(testing_bits, 2) % 42 + 1
9. run_lotto(instructions, shots=36)
10. main:Place quantum moves+Place six bets on the table
11. 验证:lotto_numbers==guess_numbers得flag
12. 关键:Lotto bits = ~Testing bits(按位取反)
13. 公式:Lotto = ((21 - (Test - 1)) % 42) + 1
14. Raw_Lotto = 63 - Raw_Test
15. Final_Lotto = (Raw_Lotto % 42) + 1
16. 需要:让test和lotto不同,但guess==lotto

## 关键 payload

```
Lotto = ((21 - (Test - 1)) % 42) + 1
```

## 经验教训

量子电路题先理解验证逻辑(entropy validation + bit extraction + 42取模),再设计电路让test和lotto不同但guess能匹配lotto;按位取反关系是常见模式。

## 标签

qiskit、quantum-circuit、Aer-simulator、qasm-simulator、QuantumCircuit、H-S-T-Z-gates、RXX-RYY-RZZ、binomialtest、entropy-validation、quantum-lotto

## 参考来源

- https://www.ctfiot.com/297316.html
- 原文件：量子安全_quantum_ctf_Qlotto_Hack_the_box.full.md
