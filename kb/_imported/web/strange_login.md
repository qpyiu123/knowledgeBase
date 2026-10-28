---
title: "strange_login"
category: web
tags: [NewStar CTF 2025, wp prose]
signals: [strange_login]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/web/strange-login.md"
tools: []
origin: imported
origin_id: official-49c1493f27f2fb9bc26913
origin_sha256: b6e0a8b80acd1df1fef51220a5a21e6522b89537326e674dbcd8c2fadf24593b
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / strange_login

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/web/strange-login.md

import Container from '@/components/docs/Container.vue'

# strange_login


本题考查简单的 SQL 注入漏洞利用。

这道题是一个典型的 SQL 注入挑战。题目描述中的 `1=1` 暗示了我们可以利用逻辑真值来绕过登录验证。我们猜测后台的 SQL 查询语句是：


这个查询语句将会把用户输入的用户名（`$user`）和密码（`$pass`）直接拼接到 SQL 语句中，没有进行任何过滤或转义，导致 SQL 注入漏洞。

我们的目标是通过注入，使 SQL 查询条件始终为真，从而绕过身份验证。常用的注入载荷是 `1' or 1=1#`，但这里需要根据查询语句的结构进行调整。

## 解题步骤

1. **理解查询结构**：查询语句是`SELECT * FROM users WHERE username = '$user' AND password = '$pass'`。我们需要在用户名或密码字段中输入特殊字符来改变查询逻辑。
2. **选择注入点**：通常，我们在用户名字段进行注入，因为密码字段可能被哈希处理（但这里没有）。假设我们在用户名输入框注入。
3. **构造注入载荷**：

- 如果我们输入用户名：`1' or 1=1#`，密码任意（例如 `123`），那么查询语句会变成：


- 解释：

  - `1'` 闭合了用户名的单引号。
  - `or 1=1` 添加了一个永远为真的条件。
  - `#` 是MySQL中的注释符，会注释掉后面的所有内容，包括 `AND password = '123'`。

- 因此，实际执行的查询是：


这个查询会返回 `users` 表中的所有行，通常登录验证会检查是否有返回结果，如果有就登录成功。

4. **实际尝试**：

- 在用户名输入框输入：`1' or 1=1#`
- 在密码输入框输入任意值（例如 `123`）。
- 点击登录，应该会成功绕过登录。

5. **为什么这样工作**：因为 `1=1` 总是真，所以查询条件永远成立，返回所有用户数据。注释符 `#` 确保了密码检查被忽略，避免了密码错误。
