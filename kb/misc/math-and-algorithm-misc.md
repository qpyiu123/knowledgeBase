---
title: 数学与算法类 misc（大数分解、矩阵、迷宫、自动机）
category: misc
tags: [math, factorization, matrix, maze, automaton, intcode]
signals: [题目给了一张地形图要求从左上走到右下, 给了一个巨大的整数要求分解或者求因子, 给出了矩阵乘法结果要求反推原矩阵, 输入里有长度上千的01序列和状态转移表, 题目说这是某个虚拟机的指令集, 附件是一个 .in 和 .out 成对的测试数据, 题目描述里出现自动机或正则或议员, 要你提交一串输入让程序输出某个值]
difficulty: hard
source: "CTF-Wiki Misc / Advent of Code 历年题 / Project Euler 大数分解 / 形式语言与自动机教材"
tools: [python, sympy, z3, gmpy2, or-tools, BFS/DFS, networkx]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是文本格式的网格（`#` 与 `.`），题面说"找到最短路径""走出迷宫"。
- 给定一个 100~300 位十进制整数，要求"分解"或"求最大公约数"或"求椭圆曲线的离散对数"。
- 给出矩阵 A 的某些向量乘积结果、或者 `A^n` 的迹，要求还原参数——**线性代数反向求解**。
- 输入是一张状态转移表 + 一个正则/图灵机描述，要求"给出能让它接受的最短字符串"。
- 题目给 `.vm` / `.asm` 之类的自定义字节码，要求"写出输入让 vm 输出 flag"。
- 场景是"当年某比赛的交互题改静态"，给了输入输出示例。
- 题目暗示"这是 NP 难但数据规模很小""枚举一下就好"。

## 二、原理

**这一类题的共同点：把"求答案"归约成"搜索问题"，关键在选对搜索算法。**

| 题型 | 数学本质 | 首选算法 |
| --- | --- | --- |
| 迷宫/网格 | 无权图最短路 | BFS（无权）、Dijkstra/A*（带权） |
| 状态空间搜索 | 有限状态图 | BFS + 状态压缩（bitset/key） |
| 大数分解 | 整数分解 | Pollard rho / ECM / Fermat（接近平方） |
| 矩阵反推 | 线性方程组 | 高斯消元（GF(p) 上）、格基约减 |
| 自动机 | 正则/DFA | 乘积自动机 + BFS 找最短接受串 |
| VM/自定义指令 | 解释器语义 | 先写解释器，再符号执行或约束求解 |
| 组合优化 | 整数规划 | 约束求解器（z3 / OR-Tools CP-SAT） |

**判定规模是最重要的一步**：状态数 < 1e6 直接 BFS；带浮点/大整数约束用 z3；NP 完全但 n 很小（< 25）直接枚举 + 剪枝或 DP 状压。

## 三、操作步骤

1. **把题目翻译成图/公式**：写下状态定义、转移函数、目标条件。迷宫题把每个格子当节点，四邻接当边。
2. **估计规模**：算一遍指数/状态数，选算法；不要上来就写 z3。
3. **先求最短/可行解，再优化**：大多数 misc 算法题只要"任意可行解"。
4. **失败时换搜索策略**：BFS → 双向 BFS → A* → IDA* → 启发式随机。
5. **大数分解**：`sympy.factorint` 先试，超过 90 位改用 `cado-nfs`/`yafu`，接近平方数先 Fermat。
6. **验证**：打印解并回代题目给定函数，确认输出与示例一致。

## 四、命令 / 脚本

```python
#!/usr/bin/env python3
# 通用网格 BFS（支持起点/终点/墙/代价）
import collections

def bfs(grid, start, goal, walls='#', moves=((1,0),(-1,0),(0,1),(0,-1))):
    R, C = len(grid), len(grid[0])
    q = collections.deque([start]); prev = {start: None}
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            path = []; cur = (r, c)
            while cur is not None: path.append(cur); cur = prev[cur]
            return path[::-1]
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != walls \
               and (nr, nc) not in prev:
                prev[(nr, nc)] = (r, c); q.append((nr, nc))
    return None

def render(path, grid, marks='.*#'):
    g = [list(r) for r in grid]
    for r, c in path: g[r][c] = '*'
    return '\n'.join(''.join(r) for r in g)

if __name__ == '__main__':
    grid = [l.rstrip('\n') for l in open('maze.txt')]
    s = grid[0].index('S'), 0
    t = grid[-1].index('E'), len(grid) - 1
    p = bfs(grid, s, t)
    print(len(p), 'steps')
    print(render(p, grid))
```

```python
#!/usr/bin/env python3
# 大数分解的三条路：sympy -> Fermat(近平方) -> Pollard rho(自实现)
import math, random
import sympy

def fermat(n, limit=10**6):
    a = math.isqrt(n)
    if a * a < n: a += 1
    for _ in range(limit):
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2: return a - b, a + b
        a += 1
    return None

def pollard_rho(n):
    if n % 2 == 0: return 2
    while True:
        c = random.randrange(1, n); f = lambda x: (x * x + c) % n
        x = y = 2; d = 1
        while d == 1:
            x = f(x); y = f(f(y)); d = math.gcd(abs(x - y), n)
        if d != n: return d

n = int(open('n.txt').read().strip())
print('sympy:', sympy.factorint(n))
f = fermat(n); print('fermat:', f)
if f is None:
    d = pollard_rho(n); print('rho:', d, n // d)
```

```python
#!/usr/bin/env python3
# 自动机：给 DFA + 禁止接受状态，BFS 找最短接受串
import collections

def shortest_accepted(delta, start, accept, alphabet='01', forbid=()):
    q = collections.deque([(start, '')]); seen = {start}
    while q:
        st, s = q.popleft()
        if st in accept: return s
        for ch in alphabet:
            ns = delta.get((st, ch))
            if ns is None or ns in forbid or ns in seen: continue
            seen.add(ns)
            q.append((ns, s + ch))
    return None

delta = {(0, '0'): 1, (0, '1'): 0, (1, '0'): 1, (1, '1'): 2, (2, '0'): 2, (2, '1'): 0}
print(shortest_accepted(delta, 0, {2}))
```

```bash
# z3 建模（约束类）
pip install z3-solver sympy gmpy2
python - <<'EOF'
from z3 import *
a, b, c = BitVecs('a b c', 8)
s = Solver(); s.add(a ^ b == 0x5a, a + c == 0x9c, b * 3 == 0x45)
print(s.check(), s.model())
EOF
```

## 五、常见坑 / 变体

- **BFS 忘了去重**：迷宫带传送门或有向边时必须 visited 去重，否则指数爆炸。
- **状态必须是完整可判定信息**：比如"拿到钥匙"才能开门的迷宫，状态要包含 `(位置, 钥匙位掩码)`，只记位置会出错误答案。
- **大数分解选错算法**：`n = p*q` 且 `p≈q` 时 Fermat 秒杀；`p,q` 差很远则先试 Pollard rho；再不行上 ECM。直接对着 200 位半素数硬刚是徒劳的。
- **矩阵题在 GF(p) 上做**：整数除法会出错，必须用模逆（`pow(x,-1,p)`），且要先确认 p 是否素数。
- **z3 的位宽**：8 位变量溢出会静默截断，约束不成立时先怀疑位宽。
- **VM 题要先写解释器**：把字节码反汇编成人类可读的伪汇编，再针对"输出 flag 的那个分支"做符号执行（angr 可参考 `angr-symbolic-execution`）。
- **复杂度陷阱**：题面说"枚举"但 n=30 时 2^n 会超时，要用 meet-in-the-middle 或 DP。
- **输出格式**：很多题要求 flag 是"路径方向串"（如 `UULLRRD`），注意映射方向。

## 六、参考来源

- [Project Euler（大数分解与数论练习_archive）](https://projecteuler.net/archives)
- [sympy 数论模块文档（factorint / isprime / discrete_log）](https://docs.sympy.org/latest/modules/ntheory.html)
- [z3 官方指南（约束求解建模）](https://microsoft.github.io/z3guide/)
- [OR-Tools CP-SAT 求解器文档](https://developers.google.com/optimization/cp/cp_solver)
- [CTF-Wiki：Misc 与脚本题思路](https://ctf-wiki.org/misc/introduction/)
