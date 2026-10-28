---
title: OSINT 工具集与语法（Google Dork）
category: osint
tags: [google dork, 高级搜索, 语法, 工具集, recon-ng, spiderfoot]
signals: [题目只给一个关键词, 需要找特定文件, 需要找某个站点的备份文件, 需要搜特定格式的文档, 需要找泄露的配置文件]
difficulty: easy
source: "CTF-Wiki 信息搜集 / Google 高级搜索官方页 / recon-ng 与 SpiderFoot 文档"
tools: [google, bing, duckduckgo, recon-ng, spiderfoot, theharvester, metagoofil, exiftool]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目只有一句话「找到这家公司的某某信息」。
- 需要找某个站点上的 `.bak`、`.git`、`.env` 文件。
- 需要找特定格式的 PDF/PPT 里的关键字。
- 需要在一大堆搜索结果里快速缩小到几条。

## 二、原理

**搜索引擎语法** 本质是把 URL/内容字段暴露成可查询的结构。常用操作符：

| 操作符 | 含义 | 例 |
| --- | --- | --- |
| `site:` | 限定域名 | `site:example.com` |
| `inurl:` | URL 中含词 | `inurl:admin` |
| `intitle:` | 标题含词 | `intitle:"index of"` |
| `intext:` | 正文含词 | `intext:"api_key"` |
| `filetype:` | 文件扩展名 | `filetype:pdf` |
| `ext:` | 同上（Bing 优先） | `ext:sql` |
| `"..."` | 精确短语 | `"internal use only"` |
| `OR` / `-` | 逻辑或 / 排除 | `(login OR signin) -site:example.com` |
| `AROUND(n)` | 邻近词（部分引擎） | `password AROUND(3) admin` |
| `*` | 通配 | `"flag{*}"` |

**"index of" 技巧**：开放目录列表服务器（nginx autoindex / Apache）会把目录内容列成 HTML，`intitle:"index of" "backup"` 能直接定位一整片可下载目录。

**工具集分工**：
- `theHarvester`：邮箱/主机/员工名（走搜索引擎 + 证书）。
- `recon-ng`：模块化框架，可链式执行（域名 → 子域 → 联系人）。
- `SpiderFoot`：自动化 200+ 模块，带 web UI 与图关系。
- `metagoofil`：批量下载某个域名的 PDF/DOC 并抽元数据。

## 三、操作步骤

1. **明确目标信息类型**（文件/邮箱/子域/凭证/代码）。
2. **构造 dork**：`site` + `filetype` + 关键字 三件套起手。
3. **多引擎交叉**：Google/Bing/DuckDuckGo 的索引差异很大。
4. **批量自动化**：小规模用脚本走 DuckDuckGo HTML 或 Bing；大规模用 recon-ng/SpiderFoot。
5. **验证**：直接打开结果页确认（不要只看摘要）。
6. **记录**：把命中的 URL、时间、证据写入报告。

## 四、命令/脚本

### 常用 dork 模板

```bash
# 目录列表
site:example.com intitle:"index of"
# 备份与配置文件
site:example.com (ext:bak OR ext:old OR ext:swp OR ext:env OR ext:sql)
# 凭据/密钥泄漏
site:example.com (intext:"api_key" OR intext:"secret_key" OR intext:"BEGIN RSA PRIVATE KEY")
# 文档泄露
site:example.com filetype:pdf (intext:"confidential" OR intext:"内部")
# Git 泄露
inurl:"/.git/config" "example.com"
# 后台与登录
site:example.com (inurl:admin OR inurl:login OR inurl:dashboard)
# 错误页泄露路径
site:example.com "Warning: mysql_connect"
# 云存储桶
site:example.com (inurl:"s3.amazonaws.com" OR inurl:"blob.core.windows.net")
# 搜 flag 本身
"flag{" site:example.com
```

### 用脚本批量搜索（DuckDuckGo HTML 端点）

```python
#!/usr/bin/env python3
# dork_run.py —— 逐条执行 dork，输出标题+URL（限速、仅公开结果）
import sys, time, urllib.parse
import requests
from bs4 import BeautifulSoup

QUERIES = sys.argv[1:] or ['site:example.com intitle:"index of"']
HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for q in QUERIES:
    print(f'\n=== {q}')
    try:
        r = requests.post('https://html.duckduckgo.com/html/',
                          data={'q': q}, headers=HEAD, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.select('a.result__a')[:10]:
            print(' -', a.get_text(strip=True)[:80], a.get('href'))
    except Exception as e:
        print('  error:', e)
    time.sleep(2)          # 限速，避免被封
```

### Bing 与 Google 备用端点

```bash
# Bing 的 filetype/站点限定
echo 'https://www.bing.com/search?q=site%3Aexample.com+filetype%3Apdf'
# Google 的 verbatim 选项（关闭个性化）
echo 'https://www.google.com/search?q=site%3Aexample.com+intitle%3Aindex+of&num=50'
# DuckDuckGo 的 HTML 版（脚本友好）
echo 'https://html.duckduckgo.com/html/?q=site%3Aexample.com'
```

### 工具链

```bash
sudo apt install -y theharvester recon-ng
theharvester -d example.com -b bing,duckduckgo,crtsh -l 200
recon-ng -w workdb1 <<'CMDS'
marketplace install all
workspaces select example
db insert domains
use recon/domains-hosts/hackertarget
set SOURCE example.com
run
show hosts
CMDS
```

```bash
# SpiderFoot（Web UI，127.0.0.1:5001）
pip install spiderfoot && python3 -m spiderfoot -l 127.0.0.1:5001
# 或用 docker
docker run -d -p 5001:5001 --name sf smicallef/spiderfoot -l 0.0.0.0:5001
```

```bash
# metagoofil：下载文档并抽元数据（作者/路径/软件版本）
pip install metagoofil
metagoofil -d example.com -t pdf,docx,xlsx -l 30 -n 20 -o out_meta
exiftool out_meta/* | grep -E 'Author|Creator|Producer|Company'
```

### 结果去重与归类

```bash
# 把多轮 dork 的 URL 汇总、去重、按扩展名分类
sort -u all_urls.txt | awk -F. '{print $NF}' | sort | uniq -c | sort -rn
grep -E '\.(bak|old|env|sql|zip|git)$' all_urls.txt
```

## 五、常见坑 / 变体

- **Google 对自动化查询限流**：用官方 Custom Search API，或放慢脚本速度。
- **`filetype:` 有索引延迟**：刚上传的文件搜不到，换 Bing/DDG。
- **爬虫屏蔽**：部分结果需要 JS 渲染，脚本只拿 HTML 会漏。
- **intitle 语法差异**：Bing 更宽松，Google 更严格。
- **合规**：只查询公开信息；发现泄露后应负责任地报告给所有者，不做进一步利用。
- **CTF 常考**：`robots.txt`、`.well-known/security.txt`、`sitemap.xml`、`/.git/`、URL 参数里的注释。

## 六、参考来源

- [CTF Wiki - 信息搜集技术](https://ctf-wiki.org/misc/recon/)
- [Google 高级搜索官方页](https://www.google.com/advanced_search)
- [DuckDuckGo 官方搜索与 API 说明](https://duckduckgo.com/)
- [recon-ng 官方仓库](https://github.com/lanmaster53/recon-ng)
- [SpiderFoot 官方仓库](https://github.com/smicallef/spiderfoot)
- [OSINT Framework - 分类工具总目录](https://osintframework.com/)
- [IntelTechniques - 搜索工具集](https://inteltechniques.com/)
