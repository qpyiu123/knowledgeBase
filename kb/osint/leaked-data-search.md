---
title: 泄漏数据检索（合法 CTF 语境下的数据聚合与验证）
category: osint
tags: [leak-data, hibp, data-breach, verification, hashes, breach-aggregator]
signals: [题目要求判断某个邮箱是否出现在公开泄漏事件里, 附件里有一份包含用户名和邮箱的 csv 转储, 题目问某个密码是否曾泄漏过, 给了哈希值要求反查对应的明文, 题目场景是一家公司发生了数据泄漏需要评估影响面]
difficulty: medium
source: "HIBP 官方 API 文档 / Have I Been Pwned 公开数据说明 / OSINT 合规使用边界公开讨论"
tools: [python, hibp-api, dehashed, crackstation, hashes-com, jq]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目给一个邮箱，问"是否出现在 XX 泄漏事件中"。
- 附件是 `users.csv`、`dump.txt`，字段是 `email,password_hash,username`。
- 题目给出一个 MD5/SHA1 哈希，要求"找出原文"。
- 场景描述"某公司数据库被拖库，请评估哪些账号受影响"。
- 题目要求"统计泄漏数据里有多少条重复记录"。
- 提示里出现 `Collection#1`、`rockyou`、`breach` 等字眼。

## 二、原理

**OSINT 语境下的泄漏数据有三类用法：**

1. **存在性验证**（最安全）：把邮箱/手机号的 SHA-1 前缀发给 HIBP 之类的服务，得到"是否泄漏"。HIBP 用的是 **k-anonymity**：只发送哈希前 5 位，服务端返回该前缀下的所有后缀，本地匹配——**服务端永远拿不到完整的哈希**。
2. **离线分析题目给的转储**：题目附件本身就是"泄漏数据"，用本地脚本做统计、去重、关联（不联网）。
3. **哈希反查**：给定哈希找明文，本质是彩虹表/字典比对，用 `hashcat -m 0` 对本地字典或在线查询（合规前提下）。

**合规边界（必须写清）**：只处理**题目明确提供或公开可验证**的数据；不下载、不传播、不交易真实泄漏库；涉及真人时只做存在性验证，不做进一步画像。

## 三、操作步骤

1. **确认数据类型**：是"目标标识符"（邮箱/用户名）还是"本地转储"。
2. **存在性验证**：对邮箱/手机号做 HIBP 查询（k-anonymity）。
3. **本地转储分析**：`csv`/`tsv` 解析，统计字段分布、重复、时间范围。
4. **关联**：用共同字段（email 或 username）把多份转储连接。
5. **哈希反查**：先判哈希类型（长度 32=MD5、40=SHA1），再字典/规则爆破。
6. **出报告**：给出"受影响账号数 + 证据 + 置信度"。

## 四、命令 / 脚本

```bash
# 1) HIBP 密码 k-anonymity 查询（只上传 SHA-1 前 5 位）
python - <<'EOF'
import hashlib, urllib.request
pw = 'Password123'
h = hashlib.sha1(pw.encode()).hexdigest().upper()
prefix, suffix = h[:5], h[5:]
url = 'https://api.pwnedpasswords.com/range/' + prefix
resp = urllib.request.urlopen(url, timeout=10).read().decode()
for line in resp.splitlines():
    s, cnt = line.split(':')
    if s == suffix:
        print('已泄漏，出现次数:', cnt); break
else:
    print('未在库中')
EOF

# 2) 邮箱泄漏查询（需要 HIBP API key）
curl -s -H "hibp-api-key: $HIBP_KEY" -H "user-agent: ctf-osint" \
  "https://haveibeenpwned.com/api/v3/breachedaccount/target@example.com?truncateResponse=false" | jq .

# 3) 本地转储统计
python - <<'EOF'
import csv, collections
rows = list(csv.DictReader(open('dump.csv', encoding='utf-8', errors='replace')))
print('总记录', len(rows), '字段', rows[0].keys())
emails = [r.get('email', '') for r in rows]
print('重复邮箱', len(emails) - len(set(emails)))
print('域名 Top5', collections.Counter(e.split('@')[-1] for e in emails).most_common(5))
EOF

# 4) 哈希反查
hashid '5f4dcc3b5aa765d61d8327deb882cf99'
hashcat -m 0 '5f4dcc3b5aa765d61d8327deb882cf99' rockyou.txt
john --format=raw-md5 --wordlist=rockyou.txt hashes.txt
```

```python
#!/usr/bin/env python3
# 泄漏转储合规分析：去重、时间范围、受影响账号清单
import csv, collections, datetime

def analyze(path, email_field='email', time_field='date'):
    rows = list(csv.DictReader(open(path, encoding='utf-8', errors='replace')))
    by_email = collections.defaultdict(list)
    for r in rows:
        e = (r.get(email_field) or '').strip().lower()
        if e:
            by_email[e].append(r)
    times = sorted(r.get(time_field) for r in rows if r.get(time_field))
    print('记录 %d，唯一邮箱 %d' % (len(rows), len(by_email)))
    if times:
        print('时间范围: %s -> %s' % (times[0], times[-1]))
    dup = {k: v for k, v in by_email.items() if len(v) > 1}
    print('重复邮箱数:', len(dup))
    for k in list(dup)[:5]:
        print('  %s x%d' % (k, len(dup[k])))
    return by_email

if __name__ == '__main__':
    import sys
    analyze(sys.argv[1])
```

## 五、常见坑 / 变体

- **HIBP 的密码接口不需要 key，账户接口需要付费 key**，别混用。
- **k-anonymity 只发前缀**：本地必须比对后缀，别把完整哈希发出去。
- **编码炸弹**：坏的 CSV 会导致解析中断，读文件一律 `errors='replace'`。
- **哈希类型判错**：32 位的也可能是 NTLM（Windows 账户），`hashid` 会给出候选，再按题目场景选。
- **撞库数据里混了假数据**：真实泄漏库有大量无效/重复条目，统计受影响账号前要清洗（邮箱格式校验）。
- **法律与伦理**：题目之外的真人数据不查、不存、不扩。
- **变体**：手机号/身份证号的部分匹配（只用于题目给定范围内）、组合泄漏（多份转储用同一 email 拼接）、哈希加盐（需先找到盐的位置）。

## 六、参考来源

- [Have I Been Pwned：官方 API 文档（k-anonymity 说明）](https://haveibeenpwned.com/API/v3)
- [HIBP 密码查询接口（Pwned Passwords）](https://haveibeenpwned.com/Passwords)
- [hashcat 官方文档（raw MD5 / NTLM 模式）](https://hashcat.net/wiki/doku.php?id=example_hashes)
- [hashid：哈希类型识别工具](https://github.com/psypanda/hashID)
- [John the Ripper 官方文档（--format 选项）](https://www.openwall.com/john/)
