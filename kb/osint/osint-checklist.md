---
title: OSINT 完整检查清单（从零到证据链）
category: osint
tags: [osint, checklist, 方法论, 证据链, 溯源流程, 报告]
signals: [题目只给一个目标名, 不知道从哪开始查, 需要写调查报告, 已经查到一些信息需要补全, 多人协作要统一流程]
difficulty: easy
source: "CTF-Wiki 信息搜集 / OSINT Framework / Bellingcat 调查方法论"
tools: [osintframework, theharvester, sherlock, fofa, crt.sh, exiftool, tineye]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一个人名/公司名/邮箱/域名，问「能找到关于它的什么信息」。
- 需要交一份「调查报告」形式的答案（若干字段）。
- 比赛里 OSINT 分值高但耗时，需要可复用的流程。
- 团队多人协查，需要明确分工与交接标准。

## 二、原理

OSINT 的核心方法论是 **"从已知量出发，沿关系边扩展，丢弃不确证的分支"**：

```
已知量（种子）
  ├─ 域名/IP  → DNS、证书、whois、资产引擎
  ├─ 邮箱     → 泄露库、Gravatar、社媒注册
  ├─ 用户名   → 跨平台枚举、头像指纹
  ├─ 人       → 公开档案、机构网站、会议名录
  └─ 图片     → 反查、EXIF、地理定位
       ↓
  每条推断都要 ≥2 条独立证据（"强证据优先"）
       ↓
  写成时间线 / 资产表 / 结论
```

**证据分级**：强（官方页面截图、DNS 记录、CT 日志）、中（第三方转载）、弱（推测、同名假设）。报告里必须标注级别。

## 三、操作步骤

1. **定义目标与产出**：要查什么字段？（姓名、邮箱、位置、资产列表…）
2. **收集种子**：题面给的字符串先做规范化（大小写、去空格、IDN 转 punycode）。
3. **逐类扩展**：按第四节清单逐条走，勾掉不再需要的分支。
4. **交叉验证**：每条结论至少两条独立来源。
5. **时间线**：把所有带时间的证据合并排序。
6. **写报告**：结论 + 证据 + 方法 + 局限。

## 四、命令/脚本

### 通用清单（按目标类型勾选）

```markdown
## A. 域名 / IP 基础设施
- [ ] whois（注册人/注册商/时间）        whois example.com
- [ ] DNS 全记录                      dig +short A/MX/NS/TXT/CNAME
- [ ] 证书透明度（子域）              crt.sh?q=%.example.com
- [ ] 资产引擎（FOFA/Shodan）          domain="example.com"
- [ ] 历史解析                        SecurityTrails / ViewDNS
- [ ] robots.txt / sitemap.xml / .well-known
- [ ] 子域枚举（被动）                subfinder -d example.com

## B. 邮箱
- [ ] 泄露库查询                      haveibeenpwned
- [ ] Gravatar 头像                   md5(email) -> gravatar.com/avatar/HASH
- [ ] 机构邮箱格式推断                firstname.lastname@
- [ ] 邮件头（如有）                  Received / Message-ID / X-Mailer

## C. 用户名 / 人员
- [ ] 跨平台枚举                      sherlock / maigret
- [ ] 头像指纹比对                    phash 对比
- [ ] 名言/写作风格检索               引号精确匹配
- [ ] 会议/论文/专利署名              Google Scholar / 专利库
- [ ] 公开代码仓库                   GitHub 提交邮箱

## D. 图片 / 位置
- [ ] EXIF（时间/相机/GPS）           exiftool -a -u -g1
- [ ] 反查（Yandex/TinEye/Lens）
- [ ] 感知哈希比对                     imagehash
- [ ] 阴影 + 时间反推纬度              suncalc / astral
- [ ] 街景比对                        Google / Mapillary
- [ ] WiFi 名称反查                   WiGLE

## E. 时间线
- [ ] WHOIS 创建/到期时间
- [ ] 证书 not_before 最早时间
- [ ] 网页快照（Wayback）
- [ ] 社媒首帖时间
```

### 一键基础侦察脚本

```bash
#!/usr/bin/env bash
# osint_basic.sh —— 域名/邮箱的快速基础侦察
set -u
T="$1"
echo "==== whois"; whois "$T" 2>/dev/null | head -25
echo "==== dns"
for r in A AAAA MX NS TXT CNAME; do printf '%-6s ' "$r"; dig +short "$r" "$T" | tr '\n' ' '; echo; done
echo "==== crt.sh"
curl -s "https://crt.sh/?q=%25.$T&output=json" | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d),'certs');print('\n'.join(sorted({x.strip() for r in d for x in r['name_value'].split('\n')})[:30]))"
echo "==== robots / sitemap"
curl -s -m 10 "https://$T/robots.txt" | head -20
curl -s -m 10 "https://$T/.well-known/security.txt" | head -10
echo "==== wayback"
curl -s "http://archive.org/wayback/available?url=$T" | head -c 300; echo
```

```bash
chmod +x osint_basic.sh && ./osint_basic.sh example.com | tee osint_example.txt
```

### Gravatar / 邮箱指纹

```bash
python -c "
import hashlib;e='TARGET_EMAIL'.strip().lower()
print('https://www.gravatar.com/avatar/'+hashlib.md5(e.encode()).hexdigest()+'?d=404&s=200')"
```

### 汇总成证据表

```python
#!/usr/bin/env python3
# evidence.py —— 把侦察结果整理成"证据-强度-来源"表（Markdown）
import sys

ROWS = [
    ("域名注册时间",     "2021-03-01", "强", "whois"),
    ("子域 admin.x.com", "存在",      "强", "crt.sh"),
    ("管理员邮箱",       "a@x.com",   "中", "网页 footer"),
    ("负责人姓名",       "张三",      "弱", "同名推断"),
]

def main():
    print("| 结论 | 值 | 强度 | 来源 |")
    print("| --- | --- | --- | --- |")
    for name, val, level, src in ROWS:
        print(f"| {name} | {val} | {level} | {src} |")
    print("\n> 只有'强'证据可直接写入最终答案；'弱'证据需交叉验证。")

if __name__ == '__main__':
    main()
```

### 快照存档（证据固化）

```bash
# 提交 Wayback 保存
curl -s "https://web.archive.org/save/https://example.com/page"
# 本地存档（防止对方删改）
wget -m -k -p --convert-links -P archive_site https://example.com/page
```

## 五、常见坑 / 变体

- **只信一条来源**：OSINT 最大的错误是"同名即同人"，必须多证据。
- **不记录时间**：截图不带时间戳以后无法证明"当时是这样"。
- **忽略时区**：跨平台时间多为 UTC，写报告要统一。
- **被反侦察**：访问真实组织站点会留下日志，CTF 里是无害的，真实调查要注意 OPSEC。
- **过度扩展**：查了 3 小时仍在扩展，应回到目标字段，及时收敛。
- **合规红线**：不查询/传播他人隐私数据，不尝试未授权访问，发现漏洞走负责任披露。

## 六、参考来源

- [CTF Wiki - 信息搜集技术](https://ctf-wiki.org/misc/recon/)
- [OSINT Framework - 按目标类型的工具树](https://osintframework.com/)
- [CTF Wiki - 取证隐写前置技术](https://ctf-wiki.org/misc/prefix/)
- [Sherlock - 用户名枚举](https://github.com/sherlock-project/sherlock)
- [crt.sh - 证书透明度查询](https://crt.sh/)
- [Wayback Machine - 网页历史快照](https://web.archive.org/)
