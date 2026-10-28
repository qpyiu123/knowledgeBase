---
title: 游戏 / 交互型 misc（概率逆推、模拟器输入、AI 对手）
category: misc
tags: [game-hacking, rng-predict, emulator, tasing, interactive, ai-opponent]
signals: [附件是一个自制小游戏需要打到某个分数才能给 flag, 服务器端 nc 连上去是一个猜数字或者 21 点游戏, 游戏随机数用的是 std::rand 或 mt19937, 题目说要连胜 20 局才能拿 flag, 游戏是 Game Boy 或 NES 的 rom 并且给了模拟器, 题目要求的输入序列必须以 .bk2 结尾, 提示里提到 slot machine 或 dice 或 poker, 游戏里有一个 AI 对手每次都能算出最优解]
difficulty: hard
source: "CTF-Wiki Misc / TASVideos BizHawk 文档 / PIE 与 MT19937 逆向 / z3 建模"
tools: [python, ctypes, z3, gdb, r2, BizHawk, FCEUX, retroarch, pwntools]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是一个可执行小游戏（Unity/Electron/Pygame/终端贪吃蛇），通关或打到分数才输出 flag。
- `nc TARGET PORT` 连上去是交互式棋牌/骰子，服务端每次随机，要求"连续赢 N 局"。
- `strings game | grep -i rand` 能看到 `rand()`、`mt19937`、`random.seed`、`srand(time(NULL))`。
- 题目给了 `.gb` / `.nes` / `.smc` ROM 与"用模拟器跑，最后提交按键序列"。
- 题目要求提交一个 `.bk2` / `.fm2` / `.m64` 录像文件，格式由模拟器定义。
- 高风险交互：每次猜错就断开，需要一次请求内完成全部回合（避免网络延迟导致状态不同步）。
- 游戏里有"对手也是程序"的描述，且它总能选最优。

## 二、原理

**游戏类 misc 的本质是"在规则确定但未知信息浮动的系统里拿确定性解"，三条主线：**

1. **预测随机数**——伪随机算法公开、种子空间小、或状态可观测。
   - `srand(time(NULL))`：种子只有约 31 位，枚举 ±3600 秒就能覆盖。
   - MT19937：输出 624 个 32 位字即可完整恢复内部状态（见 `random-mt19937`），Python `random` 用的是它。
   - LCG / xorshift：少量输出即可解方程。
2. **模拟器输入（TAS）**——把"每帧的按键状态"当作可搜索变量，用模拟器的快进与状态存档做 BFS/随机搜索，直到通关。
3. **AI 对手逆推**——对手是启发式/极小化极大，就用它的评估函数反推在所有候选中的排序，构造"它必输"的输入。

## 三、操作步骤

1. **先通关再看奖励**：很多题的通关条件可被内存修改直接满足（Cheat Engine / Frida）。
2. **随机数取证**：在 `srand`/`seed` 下断点，看种子来源；若是时间戳，写脚本枚举并比对第一局结果。
3. **模拟器路线**：确认 ROM 平台 → 找到"通关判定"的内存地址 → 用 Lua 脚本（BizHawk）读地址并做随机输入搜索。
4. **交互路线**：`pwntools` 一次性 parse 状态并本地算最优解，避免多次往返。
5. **验证**：本地复现服务器 RNG 逻辑，比对输出序列与前若干局完全一致再提交。

## 四、命令 / 脚本

```bash
# 动态逆向：找 srand/time 调用点
rabin2 -i game | grep -iE 'srand|rand|time'
gdb -q ./game -ex 'b srand' -ex 'b rand' -ex run
# 或者用 ltrace
ltrace -e 'rand+srand+time' ./game 2>&1 | head -20
```

```python
#!/usr/bin/env python3
# 时间种子枚举：给定游戏第一局输出，倒推 srand(time) 的种子
import ctypes, time

libc = ctypes.CDLL("libc.so.6")

def first_rand(seed, n=1):
    libc.srand(seed)
    return [libc.rand() for _ in range(n)]

def guess_seed(observed, window=7200):
    now = int(time.time())
    for t in range(now - window, now + window):
        # 常见用法：rand() % M
        for M in range(2, 101):
            if [x % M for x in first_rand(t, len(observed))] == observed:
                return t, M
    return None

if __name__ == '__main__':
    print(guess_seed([3, 7, 1, 9, 5]))
```

```python
#!/usr/bin/env python3
# pwntools：一次连接内完成多回合（本地先算出全部答案）
from pwn import remote, context
context.log_level = 'info'

io = remote('TARGET', 1337)
io.recvuntil(b'round 1')
answers = []          # 由本地复现的 RNG 预先生成
for i, ans in enumerate(answers):
    io.recvuntil(b'guess> ')
    io.sendline(str(ans).encode())
    ret = io.recvline()
    if b'lose' in ret:
        print('回合 %d 失败：%r' % (i, ret)); break
print(io.recvall(timeout=3).decode(errors='replace'))
```

```python
#!/usr/bin/env python3
# MT19937 状态恢复（当游戏用 python random 时）
import random

def recover_from_integers(vals):
    """vals: 624 个 32 位输出，直接还原状态"""
    assert len(vals) == 624
    r = random.Random()
    r.setstate((3, tuple([int(v) & 0xffffffff for v in vals] + [624]), None))
    return r

def crack_from_getrandbits(x, count_bits, n=624):
    """vals 是 getrandbits(B) 输出时，需要 B<=32 且收集足够样本后解线性方程组，
    实际做法见 random-mt19937 条目；此处给出 32bit 直取版的快速路径。"""
    raise NotImplementedError

if __name__ == '__main__':
    r = recover_from_integers([random.getrandbits(32) for _ in range(624)])
    print(hex(r.getrandbits(32)))
```

```lua
-- BizHawk Lua：随机搜索输入直到过关（以 GB 贪吃蛇型关卡为例，需自行改地址）
local keys = { "Up", "Down", "Left", "Right" }
local function try_once()
  local seq = {}
  for i = 1, 600 do seq[i] = keys[math.random(#keys)] end
  savestate.loadslot(1)
  for i = 1, #seq do
    joypad.set({ [seq[i]] = true }, 1)
    emu.frameadvance()
    if mainmemory.read_u8(0xC0A4) == 1 then   -- 假设 1 = 过关
      return seq
    end
  end
  return nil
end
math.randomseed(os.time())
for attempt = 1, 100000 do
  local s = try_once()
  if s then print("FOUND at " .. attempt); return end
end
```

## 五、常见坑 / 变体

- **不要"看"随机，要"复现"**：先确认算法（C 的 `rand` 与 Python 的 `random` 完全不同），再谈预测。
- **`rand()` 的实现随 libc 变**：glibc 用的是 `random()` 的同期算法（TYPE_3），musl 的实现也不同，跨平台复现要带原始 libc。
- **服务器 RNG 在进程启动时播种**：多连接共享同一个 RNG 状态，可以在一个连接里"试探"来推进序列，但要小心别的选手干扰。
- **模拟器输入帧对齐**：TAS 的输入是"每帧"的，`frameadvance` 的次数与真实帧一致，多一帧就错位。
- **ROM 的 checksum/防作弊**：真实商业 ROM 有存档校验，修改存档可被检测；自制 CTF ROM 基本无此问题。
- **交互脚本读到超时**：`recvuntil` 的 token 必须与服务器完全一致（多空格都会卡住），先用 `nc` 手工跑一遍抓真实格式。
- **游戏里藏 flag 的方式**：终端游戏可能直接用 `\033[2J` 清屏前打印，重定向输出到文件即可捡到。
- **变体**：Steam 游戏存档题（改 `.sav` 二进制）、Unity `PlayerPrefs`、Bevy/Godot 的 `.cfg`。

## 六、参考来源

- [TASVideos：工具与 BizHawk 文档（帧级输入与 savestate）](https://tasvideos.org/Bizhawk)
- [pwntools 官方文档（交互式脚本）](https://docs.pwntools.com/en/stable/)
- [rand(3) Linux man page（含 glibc 算法说明）](https://man7.org/linux/man-pages/man3/rand.3.html)
- [z3 官方指南（用于反推对手策略的约束建模）](https://microsoft.github.io/z3guide/)
- [CTF-Wiki：Misc 逆向类与游戏题](https://ctf-wiki.org/misc/introduction/)
