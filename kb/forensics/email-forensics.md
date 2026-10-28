---
title: 邮件取证（EML/PST 解析、附件提取、收发链路）
category: forensics
tags: [email, eml, pst, msg, mime, attachments]
signals: [附件是 eml msg 或者 pst 文件, 题目问谁给谁发了邮件, 邮件源码里有 base64 和 quoted-printable 混排, 要求提取附件里的压缩包, 邮件头里有 Received 长链条需要还原路由, 附件是被分段编码的多个二进制块, 题目说这封邮件是钓鱼邮件]
difficulty: medium
source: "RFC 5322 邮件格式 / RFC 2045-2049 MIME / libpff（pst-utils）文档"
tools: [python, readpst, pffexport, msgconvert, exchange-email-extractor, 7z, exiftool]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.eml` / `.msg` / `.pst` / `.ost` / `.mbox`。
- 题面说"运维收到一封可疑邮件""找出附件中的恶意文件"。
- 打开是纯文本，含 `Return-Path:`、`Received:`、`Content-Type: multipart/mixed; boundary="----=_Part_0"`。
- 正文里有 `=E4=BD=A0` 这种 QP 编码，或者 `Content-Transfer-Encoding: base64` 后跟一大段 base64。
- PST 文件几个 GB，`file` 显示 `Microsoft Outlook Personal Storage`。
- 题目要求还原"邮件里的图片""附件内的 flag"，但直接打开看不到附件。

## 二、原理

- **EML = RFC 5322 头 + MIME 体**：头是 `Key: Value`，遇到空行后是 body。MIME 用 `boundary` 分隔各段，每段自带 `Content-Type` 与 `Content-Transfer-Encoding`。
- **`Received` 头是倒序的**：最上面的 `Received` 是**最后一跳**（离你最近），最下面的是起点。每行含 `from/by ... with ... id ...; date`，逐行自上而下读就是投递路径的倒放。
- **PST**：Outlook 的专有容器，libpff 能解析出消息、附件、联系人、日历与**已删除项**（`Deleted Items` 与 recoverable items）。
- **`.msg`**：OLE 复合文档（`D0 CF 11 E0`），可以用 `olefile` 或 `msgconvert` 转成 eml。
- **附件抽取的通用思路**：识别 MIME 段 → 按其 `Content-Transfer-Encoding` 解码 → 得到原始字节 → `file` 判类型。
- **钓鱼特征**：`Received` 跳数与发件人声称的域不匹配、`Return-Path` 与 `From` 域不同、`Authentication-Results` 里 `spf=softfail`/`dmarc=fail`、附件是 `.docm`/`.lnk`/`.zip` 带密码。

## 三、操作步骤

1. **先看头**：`head -60 mail.eml`，拿到 `From/To/Subject/Date/Message-ID/Received`。
2. **验证认证结果**：找 `Authentication-Results`、`ARC-Authentication-Results`、`DKIM-Signature`。
3. **MIME 拆解**：用 `python email` 库递归遍历 `walk()`，打印每个 part 的类型与文件名。
4. **附件落盘**：按 `get_filename()` 命名，若文件名乱码，用 `email.header.decode_header` 还原（`=?UTF-8?B?...?=`）。
5. **PST/OST**：`pffexport -m all mail.pst`，或 `readpst -m -o out mail.pst`（也支持 `-D` 导出已删除邮件）。
6. **`.msg`**：`msgconvert mail.msg`。
7. **交叉验证**：邮件里的图片/文档用 `exiftool` 看创建者与时间，判断是否伪造。

## 四、命令 / 脚本

```bash
# 头部速览
head -60 mail.eml
grep -iE '^(from|to|cc|subject|date|message-id|return-path|authentication-results):' mail.eml
grep -c '^Received:' mail.eml
# PST / OST / MSG
pffexport -m all -f mail.pst          # 输出 mail.export/ 目录
readpst -D -m -o out mail.pst         # -D 含已删除项
msgconvert mail.msg
# 已经抽出的附件文件
find out -type f -exec file {} \;
```

```python
#!/usr/bin/env python3
# EML 递归解析：头部、正文、附件一并落地
import email, email.policy, os, sys, pathlib

def dump(path, outdir='mail_out'):
    pathlib.Path(outdir).mkdir(exist_ok=True)
    msg = email.message_from_bytes(open(path, 'rb').read(), policy=email.policy.default)
    for h in ('From', 'To', 'Subject', 'Date', 'Return-Path'):
        print('%-13s %s' % (h + ':', msg.get(h)))
    print('Received 跳数:', len(msg.get_all('Received') or []))
    # 倒序打印投递路径（从起点到终点）
    for i, r in enumerate(reversed(msg.get_all('Received') or [])):
        print('  hop%02d %s' % (i, r.replace('\n', ' ')[:140]))
    n = 0
    for part in msg.walk():
        ctype = part.get_content_type()
        fname = part.get_filename()
        if fname:
            data = part.get_payload(decode=True) or b''
            dst = os.path.join(outdir, fname.replace('/', '_'))
            open(dst, 'wb').write(data)
            print('附件 ->', dst, len(data), 'bytes')
            continue
        if ctype == 'text/plain':
            txt = part.get_content()
            print('---- text/plain ----')
            print(txt[:800])
            n += 1

if __name__ == '__main__':
    dump(sys.argv[1])
```

```bash
# 附件的深度处理：抽出的 zip/文档继续走文件流程
for f in mail_out/*; do
  echo "== $f"; file "$f"; 7z l "$f" 2>/dev/null | head -5
done
# .msg 的 OLE 结构
python -c "
import olefile
o = olefile.OleFileIO('mail.msg')
print('\n'.join('/'.join(s) for s in o.listdir()))
"
```

## 五、常见坑 / 变体

- **`Content-Transfer-Encoding: 7bit` 的文章里其实藏着 base64**：有些题把 base64 直接写进正文（不声明编码），先正则抓 `[A-Za-z0-9+/=]{40,}` 再解。
- **`Received` 顺序读反**：很多人从下往上读到"第一跳"就停了，实际上最上面的才是最终网关，end-to-end 判断要看全部。
- **附件名伪装**：`Content-Type: image/png` 但内容是 `MZ` 或 `PK`，不要信头里的 type，以 `file` 结果为准。
- **多段边界嵌套**：`multipart/related` 里套 `multipart/alternative`，要递归 `walk()` 而不是只遍历顶层。
- **PST 里的已删除邮件**：`pffexport -m all` 不含回收站，需 `-m recoverable` 或 `readpst -D`。
- **时区**：`Date:` 头带 `+0800`，`$Received` 里可能是 UTC，交叉比较前统一换算。
- **变体**：`.msg` 转 eml 后再走同一流程；`.mbox` 用 `mail.box`/`mb2md` 拆分；Thunderbird profile 里的 `Inbox`（无扩展名 mbox）。

## 六、参考来源

- [RFC 5322：Internet Message Format](https://www.rfc-editor.org/rfc/rfc5322)
- [RFC 2045：MIME 第一部分（传输编码）](https://www.rfc-editor.org/info/rfc2045/)
- [libpff / pst-utils：PST 解析与 pffexport 用法](https://github.com/libyal/libpff)
- [PST 取证实战：pffexport 提取附件与已删除项](https://abdurrehmanrehan.medium.com/immersive-labs-cyber-million-incident-response-parsing-pst-write-up-108978b93675)
- [Python email 库文档（policy.default 与 get_content）](https://docs.python.org/3/library/email.html)
