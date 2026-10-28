---
title: "[原创] STL 容器逆向与实战 (N1CTF 2022 cppmaster wp)"
category: misc
tags: ["N1CTF 2022", "misc", "stl_reversing", "llvm_pass_dump", "deque_iterator_memory", "vector_three_pointer"]
signals: ["N1CTF 2022 2022", "stl_reversing", "llvm_pass_dump", "deque_iterator_memory", "vector_three_pointer", "rb_tree_node_color", "hashtable_buckets", "string_local_buf_8", "recursive_stl_containers", "misc_unknown", "N1CTF", "cppmaster", "LLVM", "Pass"]
difficulty: hard
source: "https://www.ctfiot.com/76880.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [原创] STL 容器逆向与实战 (N1CTF 2022 cppmaster wp)

> 赛事：N1CTF 2022 2022 | 方向：misc | 难度：hard | 工具：C

## 一句话总结

N1CTF 2022 cppmaster 逆向：LLVM Pass dump class 结构，deque<map<unordered_map>> 三层嵌套 STL 容器 + 动调 input_check 函数确认嵌套顺序 + 还原数据。

## 攻击链

1. LLVM IR pass DumpClass dump 类型 → class.std::deque<string> { map/size/start/finish iterator(cur/first/last/map) } → class.std::vector<string> { start/finish/end_of_storage } → class.std::map<string,string> { _Rb_tree key_compare + header(node color/parent/left/right) + node_count } → class.std::unordered_map { buckets[]+bucket_count+element_count+_Prime_rehash_policy } → class.std::string { ptr + string_length + union{allocated_capacity, local_buf[8]} → cppmaster:deque<map<int,int>><<rb_tree>> → input_check 数字 → step1 step2 跨层 → 还原嵌套类型 + 数据

## 关键 payload

```
deque 三件套 (map/size + start/finish iterator) / vector 三指针 (start/finish/end_of_storage) / rb_tree 5 字段 (color/parent/left/right) + node_count / hashtable (buckets[]+bucket_count+element_count) / string (ptr+length+local_buf[8])
```

## 经验教训

STL 容器逆向先识别底层数据结构 (rb_tree/deque/hashtable/vector/string) 再识别模板类型；LLVM Pass dump 是学习 C++ 类内存模型的黄金工具。

## 标签

stl_reversing、llvm_pass_dump、deque_iterator_memory、vector_three_pointer、rb_tree_node_color、hashtable_buckets、string_local_buf_8、recursive_stl_containers、ctf_n1ctf、cplusplus_re

## 参考来源

- https://www.ctfiot.com/76880.html
- 原文件：[原创]STL容器逆向与实战(N1CTF2022_cppmaster_wp).full.md
