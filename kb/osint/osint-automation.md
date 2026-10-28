---
title: OSINT 自动化（脚本化收集与结果落盘）
category: osint
tags: [automation, recon, subfinder, httpx, reconftw, rate-limit]
signals: [题目要求对一个域名做全面信息收集, 需要快速把几百个子域名的存活情况摸清楚, 要批量查询多个 whois 和 dns 记录, 题目分在 osint 但目标明确给了范围, 需要把结果整理成表格提交, 人力手工查太慢想写脚本]
difficulty: medium
source: "ProjectDiscovery 官方文档（subfinder/httpx）/ reconFTW 文档 / 公开被动 DNS 数据源说明"
tools: [python, subfinder, httpx, amass, dig, whois, jq, reconftw]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目给一个域名/公司名，要求"找出所有关联资产"。
- 需要提交"子域名列表""开放端口""证书主题"作为答案。
- 范围有明确边界（`*.example.com`），适合脚本化。
- 题目要求"找出某个特定服务"，人工逐个点太慢。
- 目标是公开可查的信息，非入侵。
- 题面提到"被动信息收集"。

## 二、原理

**自动化 OSINT 的三段式：采集 → 归一 → 输出。**

1. **采集**：调用公开数据源（证书透明度日志、被动 DNS、搜索引擎 API、WHOIS）。
   - **crt.sh**：CT 日志里的证书会包含 `SAN`（Subject Alternative Name），是子域名最富集的来源。
   - **subfinder**：聚合几十个被动源，纯被动、不直接打目标。
   - **httpx**：对候选域名做存活探测，抓标题与指纹。
2. **归一**：统一成 `(host, port, title, tech, first_seen)` 的表格。
3. **输出**：CSV/JSON，便于人工筛选。

**自动化必须遵守的边界**：只做被动/公开数据查询；不做目录爆破、漏洞扫描、登录爆破（那是 Web 范畴，属于主动攻击）。

## 三、操作步骤

1. **圈定范围**：`example.com` 与允许的子域。
2. **被动子域采集**：`subfinder` + `crt.sh` 双源，合并去重。
3. **存活探测**：`httpx` 批量请求，拿到状态码/标题/技术栈。
4. **DNS 补充**：`dig` 查 MX、TXT（常含 SPF 里的 IP 段与验证记录）。
5. **归属确认**：WHOIS + IP 反查 ASN，确认是否真的属于目标。
6. **落盘与复盘**：输出 CSV，标注每条数据的来源与时间。

## 四、命令 / 脚本

```bash
# 被动子域（ProjectDiscovery）
subfinder -d example.com -all -silent -o subs.txt
# 证书透明度（crt.sh）
curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' | tr ',' '\n' | sed 's/\*\.//' | sort -u >> subs.txt
# 合并去重
sort -u subs.txt -o subs.txt
# 存活与指纹
httpx -l subs.txt -sc -title -tech-detect -silent -o live.txt
# DNS 记录
dig +short MX example.com
dig +short TXT example.com
dig +short NS example.com
# WHOIS 与归属
whois example.com | grep -iE 'registrar|creation|expiry|name server'
```

```python
#!/usr/bin/env python3
# 一体化被动收集（纯公开接口，带限速与缓存）
import json, time, urllib.request, urllib.parse, csv, os, sys

UA = {'User-Agent': 'ctf-osint/1.0 (educational)'}
CACHE = 'osint_cache'

def get(url, key, sleep=1.0):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, key)
    if os.path.exists(p):
        return open(p, 'rb').read()
    req = urllib.request.Request(url, headers=UA)
    try:
        data = urllib.request.urlopen(req, timeout=15).read()
    except Exception as e:
        print('[-] %s: %s' % (url, e))
        return b''
    open(p, 'wb').write(data)
    time.sleep(sleep)
    return data

def crtsh(domain):
    url = 'https://crt.sh/?q=' + urllib.parse.quote('%.' + domain) + '&output=json'
    raw = get(url, 'crt_%s.json' % domain)
    names = set()
    try:
        for row in json.loads(raw or b'[]'):
            for n in row.get('name_value', '').split('\n'):
                n = n.strip().lower().lstrip('*.')
                if n.endswith(domain):
                    names.add(n)
    except Exception as e:
        print('[-] crtsh parse: %s' % e)
    return sorted(names)

def dns_records(domain):
    out = {}
    for t in ('A', 'MX', 'TXT', 'NS'):
        url = 'https://dns.google/resolve?name=%s&type=%s' % (domain, t)
        raw = get(url, 'dns_%s_%s.json' % (domain, t), sleep=0.3)
        try:
            out[t] = [a.get('data') for a in json.loads(raw or b'{}').get('Answer', [])]
        except Exception:
            out[t] = []
    return out

def main(domain):
    subs = crtsh(domain)
    print('crt.sh 子域 %d 个' % len(subs))
    recs = dns_records(domain)
    for k, v in recs.items():
        print('%-3s %s' % (k, v[:6]))
    with open('subdomains.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['subdomain', 'source'])
        for s in subs:
            w.writerow([s, 'crt.sh'])
    print('已写出 subdomains.csv')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'example.com')
```

```bash
# reconFTW：把一堆被动+轻量主动步骤串起来（注意只对授权目标）
reconftw -d example.com -r -s   # -r 只 recon，-s 跳过子域爆破
# 结果在 reconftw/example.com/ 下按阶段分目录
```

## 五、常见坑 / 变体

- **限速与封禁**：crt.sh 对高频请求返回 502，必须加 sleep 与本地缓存（脚本里已实现）。
- **通配符子域**：`*.example.com` 会把任意子域都解析成同一个 IP，要先用随机子域探测通配，命中的结果要剔除。
- **CT 日志的时延**：新证书要几小时到一天才进 `crt.sh`。
- **不要把扫描器指向目标**：CTF 场景里多数环境禁止主动扫描，先读规则。
- **多源冲突**：不同源给出的 IP 不一致时，用 DNS 的实际解析作准。
- **变体**：ASN/CIDR 反查（`amass intel -asn`）、证书序列号关联、`favicon` 哈希反查同源系统。

## 六、参考来源

- [subfinder 官方仓库（被动子域枚举）](https://github.com/projectdiscovery/subfinder)
- [httpx 官方仓库（存活探测与技术指纹）](https://github.com/projectdiscovery/httpx)
- [crt.sh：证书透明度日志查询接口](https://crt.sh/)
- [reconFTW：自动化侦察框架](https://github.com/six2dez/reconftw)
- [Google Public DNS 的 DoH JSON 接口说明](https://developers.google.com/speed/public-dns/docs/doh)
