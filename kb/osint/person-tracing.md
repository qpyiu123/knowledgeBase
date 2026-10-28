---
title: 人员溯源（LinkedIn/GitHub/邮箱信息聚合）
category: osint
tags: [person-osint, github, linkedin, email, username, footprint]
signals: [题目给出了一个用户名要求找他所有的社交账号, 给了邮箱地址要求推断真名或者公司, 题目目标是一个开发者的 github 主页, 要求从招聘网站或者简历推断学历经历, 需要把多个平台的账号关联到同一个人, 题目给了头像要求反向搜索出身份]
difficulty: medium
source: "OSINT 公开工具文档（holehe/sherlock/maigret）/ GitHub API 文档 / CTF OSINT 真题"
tools: [python, holehe, sherlock, maigret, github-api, epieos, whatsmyname]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题面给出一个 `username`（如 `zer0day_42`），要求"找出他的真实身份"。
- 给出 `email@example.com` 或一段邮箱片段，要求推断注册过的平台。
- 题目目标人物是"某开源项目作者""某公司员工"。
- 要求"找一个时间点他发过的一条推文/commit"。
- 题面给了头像、昵称、城市片段等零散信息。
- 需要给出"生日/毕业院校/公司"作为答案。

## 二、原理

**人员溯源的本质是"用同一个标识符在不同平台间跳转"，逐步提高唯一性。**

- **用户名复用**：大多数人跨平台用同一个昵称，`sherlock`/`maigret` 在数百个站点同名探测，工业级工具有 3000+ 站点规则。
- **邮箱 → 账号**：`holehe` 利用"忘记密码"接口判断该邮箱是否在某平台注册（不发送重置邮件，只解析响应差异）。
- **GitHub 是高价值节点**：public email、commit 的 author 字段（含作者名与邮箱）、`/users/{u}/events`（最近活动）、gist、fork 关系、star 行为都会泄露兴趣与身份。
- **跨平台桥接**：同一张头像哈希、同一段个人简介、同一批关注者，都是"同一人"的证据。
- **时间线一致性**：同一个人不同平台的时间戳（时区、活跃时段）能反向印证"是否同一人"。

## 三、操作步骤

1. **以用户名起手**：`sherlock`/`maigret` 全平台扫描，得到账号列表。
2. **以邮箱补充**：`holehe` 判断注册平台；`epieos` 类服务查 Google 关联。
3. **GitHub 深挖**：`/users/{u}` 读 `name`、`company`、`blog`、`location`；`/users/{u}/events/public` 看活动；`git log --format` 看 commit 邮箱。
4. **社交平台**：把上面得到的真名/公司拿去 LinkedIn、Twitter 交叉。
5. **证据归并**：建一张表"平台 / 标识符 / 证据 / 置信度"。
6. **收敛**：只保留能互相印证的账号，其余标记为"同名不同人"。

## 四、命令 / 脚本

```bash
# 用户名跨平台
pip install maigret
maigret zer0day_42 --html
sherlock zer0day_42 --timeout 5 --print-found

# 邮箱注册平台探测
pip install holehe
holehe target@example.com

# GitHub API
curl -s https://api.github.com/users/zer0day_42 | jq '{name,company,blog,location,email,created_at}'
curl -s "https://api.github.com/users/zer0day_42/events/public?per_page=30" | jq '.[] | {type, repo: .repo.name, created_at}'
curl -s "https://api.github.com/users/zer0day_42/repos?per_page=100" | jq -r '.[] | "\(.name) \(.language) \(.pushed_at)"'
```

```bash
# commit 里的邮箱与作者名（最硬的个人信息来源）
git clone --depth 200 https://github.com/zer0day_42/repo.git
git log --format='%an <%ae> %ad' --date=iso | sort -u | head -20
# 找同一人跨仓库的唯一邮箱
git log --all --format='%ae' | sort | uniq -c | sort -rn | head
```

```python
#!/usr/bin/env python3
# 多平台结果归并：按"昵称/头像哈希/简介"打分，判断是否同一人
import hashlib, json, urllib.request

def img_hash(url):
    try:
        d = urllib.request.urlopen(url, timeout=10).read()
        return hashlib.md5(d).hexdigest()[:12]
    except Exception:
        return None

def same_person(a, b):
    score = 0
    if a.get('name') and a['name'] == b.get('name'):
        score += 3
    if a.get('bio') and a['bio'] == b.get('bio'):
        score += 3
    if a.get('avatar') and b.get('avatar'):
        if img_hash(a['avatar']) == img_hash(b['avatar']):
            score += 4
    if set(a.get('links', [])) & set(b.get('links', [])):
        score += 2
    return score

if __name__ == '__main__':
    a = {'name': 'Zhang San', 'bio': 'reverse engineer', 'avatar': 'https://example.com/a.png',
         'links': ['https://blog.example.com']}
    b = {'name': 'Zhang San', 'bio': 'reverse engineer', 'avatar': 'https://example.com/a.png',
         'links': []}
    print('相似度:', same_person(a, b))
```

```bash
# 常见平台的手工跳转路径（拿到用户名后逐个试）
# https://github.com/<u>          / https://x.com/<u>
# https://www.zhihu.com/people/<u> / https://weibo.com/<u>
# https://keybase.io/<u>         <- 能直接绑定多个社交账号，极高价值
# https://www.instagram.com/<u>
```

## 五、常见坑 / 变体

- **同名不同人**：`sherlock` 的命中只是"该昵称存在"，不等于同一人，必须靠头像/简介/时间线交叉。
- **API 速率限制**：GitHub 未认证 60 次/小时，带 token 5000 次/小时；批量查要先申请 token 并加退避。
- **邮箱隐藏**：GitHub 用户可用 `noreply@github.com` 别名，`git log` 里看到的是 ID 而不是真实邮箱。
- **时区线索**：commit 的 `%ad` 带本地时区偏移，能反推人物所在时区。
- **CTF 场景**：题目目标通常是虚构 ID，答案多为"平台上某个用户名/生日/城市"，以题面提示为准。
- **伦理边界**：只做题目指定目标、公开信息，不碰私密账户与真实个人隐私。
- **变体**：`WhatsMyName`（站点列表）、`maigret` 的递归模式（从线索再扩散）、`keybase` 的加密身份绑定。

## 六、参考来源

- [holehe：邮箱注册平台探测工具](https://github.com/megadose/holehe/)
- [sherlock：用户名跨平台检索](https://github.com/sherlock-project/sherlock/)
- [maigret：更强的用户名 OSINT 工具（含递归）](https://github.com/soxoj/maigret)
- [GitHub REST API：users 与 events 接口](https://docs.github.com/en/rest/users/users)
- [WhatsMyName：账号存在性检测的站点规则集](https://whatsmyname.app/)
