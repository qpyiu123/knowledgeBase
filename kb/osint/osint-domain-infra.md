---
title: 域名 / IP / 证书溯源（FOFA、Shodan、crt.sh）
category: osint
tags: [域名, ip, 证书透明度, fofa, shodan, crt.sh]
signals: [题目给了一个域名, 需要找同一实体的其他资产, 需要找子域名, 需要证书信息, 需要找 ip 归属, 收录了某个关键词的资产]
difficulty: easy
source: "CTF-Wiki 信息搜集 / crt.sh 证书透明度 / Shodan 文档 / FOFA 语法说明"
tools: [crt.sh, shodan, fofa, censysearch, whois, dig, subfinder, amass, dnsdumpster]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一个域名 `example.com`，要求「找到同源的其他域名/子域」。
- 题干提到「该公司还暴露了哪些服务」。
- 需要根据证书里的组织名反查归属。
- 需要查某个 IP 段下的所有 Web 服务。

## 二、原理

**证书透明度（Certificate Transparency, CT）**：所有公开 CA 签发的 TLS 证书都要记入公开日志。**crt.sh** 就是 CT 日志的搜索引擎，可以按域名、组织名、证书序列号搜索，是挖子域名的**最高性价比**手段（一次性拿到历史签发记录）。

**搜索资产引擎**：
| 引擎 | 特色 | 常用语法 |
| --- | --- | --- |
| FOFA | 中国区资产多，支持复杂逻辑 | `domain="x.com"`、`cert="Org"`、`body="关键字"` |
| Shodan | 全球设备指纹、banner | `org:"X"`、`http.title:"X"`、`ssl:"X"` |
| Censys | 证书与服务 | `services.tls.certificates.leaf_data.issuer.organization="X"` |
| ZoomEye | 中英文混合 | `app:"nginx"`、`hostname:"x.com"` |

**DNS 侧**：`dig` 拿 A/CNAME/MX/TXT；NS 记录常指向同一托管商；`TXT` 里可能有 SPF 暴露的云厂商。**WHOIS** 给出注册人与注册商（隐私保护后信息有限）。

## 三、操作步骤

1. **DNS 全量记录**：`dig ANY`，`A/AAAA/MX/NS/TXT/CNAME/SOA` 都看。
2. **证书透明度**：`crt.sh` 按域名与组织名搜索，列出所有子域。
3. **资产引擎**：FOFA/Shodan 用 `domain=` 或 `cert=` 关联。
4. **IP 归属**：`whois` + `ipinfo`，再看同 C 段的邻居（Shodan `net:1.2.3.0/24`）。
5. **历史记录**：SecurityTrails / ViewDNS 看历史解析（可发现已下线资产）。
6. **汇总**：把子域名/证书/组织名交叉验证，产出"同一实体资产图"。

## 四、命令/脚本

### DNS 与 WHOIS

```bash
dig +short A example.com
dig +short MX example.com
dig +short NS example.com
dig +short TXT example.com            # SPF/DKIM 常暴露云厂商
dig +short CNAME www.example.com
whois example.com | head -30
whois 1.2.3.4 | grep -iE 'netname|orgname|country'
```

### crt.sh（证书透明度）

```bash
# 网页：https://crt.sh/?q=%25.example.com
curl -s 'https://crt.sh/?q=%25.example.com&output=json' | \
  python -c "
import sys, json
rows = json.load(sys.stdin)
names = sorted({n.strip() for r in rows for n in r['name_value'].split('\n')})
print(len(names), 'unique names')
for n in names[:40]: print(n)"
# 按组织名查（找同一实体签的所有证书）
curl -s 'https://crt.sh/?q=%22TARGET+ORG%22&output=json' | head -c 600
```

### FOFA（需 API Key 或网页查询）

```bash
# 网页
echo 'https://fofa.info/result?qbase64='$(echo -n 'domain="example.com"' | base64)
# API
curl -s "https://fofa.info/api/v1/search/all?email=EMAIL&key=FOFA_KEY&qbase64=$(echo -n 'cert="example.com" && port="443"' | base64)&size=20"
```

### Shodan

```bash
pip install shodan
shodan init SHODAN_API_KEY
shodan search 'org:"TARGET ORG"'
shodan search 'ssl.cert.subject.CN:"example.com"'
shodan host 1.2.3.4
shodan search 'net:1.2.3.0/24 http.title:"admin"'
# 命令行查关键字与统计
shodan stats --facets country 'org:"TARGET ORG"'
```

### 子域名枚举

```bash
pip install subfinder
subfinder -d example.com -silent | sort -u | tee subs.txt
# 被动 + 证书 + DNS 暴力（amass 更全但慢）
amass enum -passive -d example.com -o amass.txt
# 验证哪些子域还活着
cat subs.txt | httpx -silent -title -tech-detect
# 只看解析到的 IP
cat subs.txt | dnsx -a -resp -silent
```

### 批量汇总成证据表

```python
#!/usr/bin/env python3
# asset_matrix.py —— 合并 crt.sh / subfinder 结果，标注来源与状态
import subprocess, json, sys, socket

domain = sys.argv[1] if len(sys.argv) > 1 else 'example.com'
names = set()

try:
    out = subprocess.run(['curl', '-s',
                          f'https://crt.sh/?q=%25.{domain}&output=json'],
                         capture_output=True, text=True, timeout=60).stdout
    for r in json.loads(out or '[]'):
        for n in r['name_value'].split('\n'):
            names.add(n.strip().lower())
except Exception as e:
    print('crt.sh failed:', e)

try:
    out = subprocess.run(['subfinder', '-d', domain, '-silent'],
                         capture_output=True, text=True, timeout=180).stdout
    names.update(x.strip().lower() for x in out.splitlines() if x.strip())
except Exception as e:
    print('subfinder failed:', e)

print(f'{len(names)} names')
for n in sorted(names):
    try:
        ips = sorted({ai[4][0] for ai in socket.getaddrinfo(n, 443)})
    except Exception:
        ips = []
    print(f'{n:45s} {" ".join(ips) if ips else "(no A record)"}')
```

## 五、常见坑 / 变体

- **`%` 通配**：`crt.sh` 里 `%.example.com` 才是"所有子域"，`example.com` 只精确匹配。
- **CT 日志有延迟**：刚签发的证书可能 1~24 小时后才被索引。
- **CDN 遮挡**：解析到 Cloudflare 会看不到源站，需要历史 DNS / 证书 SAN / 邮件头。
- **子域名枚举合规**：只做被动查询（不发爆破包）最安全；主动爆破要确保获得授权。
- **FOFA/Shodan 需要账号**：免费额度有限，语法差异大（FOFA 是 `domain=`，Shodan 是 `org:`）。
- **同 IP 反查**：共享主机上一个 IP 可能挂几十个站，`hostname:` 反查更有意义。
- **CTF 常见输出**：flag 通常是某个隐藏子域名的 TXT 记录或页面标题。

## 六、参考来源

- [CTF Wiki - 信息搜集技术](https://ctf-wiki.org/misc/recon/)
- [crt.sh - 证书透明度日志搜索](https://crt.sh/)
- [Shodan 官方站](https://www.shodan.io/)
- [FOFA 网络空间测绘](https://fofa.info/)
- [subfinder - 被动子域名枚举](https://github.com/projectdiscovery/subfinder)
- [OSINT Framework（域名/基础设施分类）](https://osintframework.com/)
