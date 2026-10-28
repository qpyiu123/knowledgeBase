---
title: 社媒溯源（账号关联 / 用户名枚举 / 图片反查）
category: osint
tags: [社媒, 用户名枚举, 账号关联, sherlock, 图片反查, 溯源]
signals: [题目给了一个用户名, 需要找到同一个人的其他账号, 需要找作者主页, 需要还原发布历史, 图片需要反查来源]
difficulty: medium
source: "CTF-Wiki 信息搜集 / Sherlock 项目 / Whatsmyname / Bellingcat 在线调查指南"
tools: [sherlock, whatsmyname, maigret, google-lens, yandex, tineye, wayback-machine]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一个用户名 `@xxx`、昵称或头像，要求「找到这个人的真实身份/其他平台账号」。
- 题干说「作者是谁」「找出同一人发布的另一张图」。
- 给了微博/知乎/GitHub 主页链接，要求扩展出更多信息。

## 二、原理

**账号关联（username pivot）**：很多人跨平台复用同一用户名/头像/简介。用工具在几百个平台批量探测同名账号存在性，再人工比对**头像哈希、简介文本、注册时间、好友关系**。

**图片反查**：不同搜索引擎的索引不同——
- Google 图片：覆盖面广，支持"找相似"。
- Yandex：**人脸与东欧/亚洲图**特别强。
- TinEye：按**图像指纹**精确匹配，能找到历史版本与首次出现时间。
- PimEyes：人脸搜索（付费，慎用于真人）。
- 百度识图：中文互联网。

**时间线**：Wayback Machine 能看历史快照；社交平台的 API/网页存档能还原发帖时间。

## 三、操作步骤

1. **收集已知量**：用户名、昵称、邮箱、头像、签名、背景图、写作风格。
2. **枚举**：`sherlock` / `maigret` 批量查同名账号。
3. **验证**：打开命中站点，比对头像（`sha256`）、简介、创建时间。
4. **扩展**：用邮箱查 `haveibeenpwned`，用头像反查，用昵称搜 Google dork。
5. **存档**：`archive.org` 保存结果，避免对方删帖后无法引用。
6. **写结论**：把证据链写清楚（哪些是强证据、哪些是推测）。

## 四、命令/脚本

### 用户名批量枚举

```bash
pip install sherlock-project
sherlock TARGET_USERNAME --output result.txt
sherlock TARGET_USERNAME --timeout 10 --print-found
# 更强的 maigret（带递归与证据聚合）
pip install maigret
maigret TARGET_USERNAME --html -a
# whatsmyname 大列表（纯网页版也可用）
```

```python
#!/usr/bin/env python3
# avatar_hash.py —— 下载多平台头像并比对哈希/感知哈希
import hashlib, io, sys
import requests
from PIL import Image

URLS = {
    'github': 'https://github.com/{u}.png',
    'gravatar': 'https://www.gravatar.com/avatar/{h}?s=200',
}

def dhash(img: Image.Image, size=8) -> str:
    img = img.convert('L').resize((size + 1, size), Image.LANCZOS)
    px = list(img.getdata())
    bits = [px[r * (size + 1) + c] > px[r * (size + 1) + c + 1]
            for r in range(size) for c in range(size)]
    return ''.join('1' if b else '0' for b in bits)

def main(user):
    for name, tpl in URLS.items():
        try:
            r = requests.get(tpl.format(u=user, h=hashlib.md5(
                user.encode()).hexdigest()), timeout=10)
            if r.status_code != 200:
                continue
            im = Image.open(io.BytesIO(r.content))
            print(f'{name}: sha256={hashlib.sha256(r.content).hexdigest()[:16]} '
                  f'dhash={dhash(im)} size={im.size}')
        except Exception as e:
            print(name, 'error', e)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'TARGET_USERNAME')
```

### 图片反查与指纹

```bash
# 本地先提指纹（结果用于跨平台比对，不上传）
python - <<'PY'
from PIL import Image
import imagehash
im = Image.open('target.jpg')
for alg in ('average_hash', 'phash', 'dhash', 'whash'):
    print(alg, getattr(imagehash, alg)(im))
PY
# 浏览器打开反查入口
echo 'https://yandex.com/images/'
echo 'https://tineye.com/'
echo 'https://lens.google.com/'
```

```bash
# Wayback 看历史版本
curl -s 'http://archive.org/wayback/available?url=TARGET_URL' | head -c 400
# 列出某 URL 的所有快照
curl -s 'http://web.archive.org/cdx/search/cdx?url=TARGET_URL&output=json&limit=20' | head -c 800
```

### 带社交痕迹的 Google dork

```bash
# 用 site: 限定平台，用引号做精确匹配
for site in site:github.com site:zhihu.com site:weibo.com site:twitter.com site:x.com; do
  echo "=== $site"
  echo "https://www.google.com/search?q=%22TARGET_USERNAME%22+$site"
done
# 反查邮箱
curl -s 'https://haveibeenpwned.com/api/v3/breachedaccount/TARGET_EMAIL' \
  -H 'hibp-api-key: API_KEY' | head -c 400
```

### 时间线还原

```python
#!/usr/bin/env python3
# timeline_merge.py —— 合并多来源时间戳成统一时间线
import json, sys
rows = []
for fn in sys.argv[1:]:
    for line in open(fn):
        try:
            d = json.loads(line)
        except Exception:
            continue
        rows.append((d.get('time', ''), d.get('source', ''), d.get('text', '')[:80]))
for t, s, txt in sorted(rows):
    print(f'{t}  [{s}] {txt}')
```

## 五、常见坑 / 变体

- **同名不同人**：必须至少两条独立强证据（头像哈希 + 简介 + 邮箱）再下结论。
- **私人账号**：不要尝试绕过隐私设置或猜测密码；只使用公开信息。
- **图片被压缩**：平台会重新压缩，感知哈希（phash）比 MD5 更鲁棒。
- **元数据被清**：上传到社交平台的图会剥离 EXIF，需依赖视觉特征。
- **假账号/仿冒**：比较注册时间与关注顺序，仿冒号往往注册很晚。
- **合规**：CTF 给的是虚构账号；真实个人请遵守当地隐私法规，不进行骚扰或公开个人信息。

## 六、参考来源

- [CTF Wiki - 信息搜集技术](https://ctf-wiki.org/misc/recon/)
- [Sherlock - 跨平台用户名枚举](https://github.com/sherlock-project/sherlock)
- [Maigret - 递归账号搜集与报告](https://github.com/soxoj/maigret)
- [Yandex 图片反查](https://yandex.com/images/)
- [TinEye 反向图片搜索](https://tineye.com/)
- [Have I Been Pwned - 邮箱泄露查询](https://haveibeenpwned.com/)
- [OSINT Framework - 工具总目录](https://osintframework.com/)
