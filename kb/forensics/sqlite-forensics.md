---
title: 数据库取证（SQLite freelist/WAL 恢复删除记录）
category: forensics
tags: [sqlite, wal, freelist, undelete, recovery, record-format]
signals: [附件是一个 sqlite3 文件或者没有扩展名的数据库, 打开发现表里数据明显变少, 同目录下还有 -wal 或 -journal 后缀的文件, 题目问被删除的记录内容是什么, 数据库文件里有大量 0x00 填充的空页, 要求还原某条已经 deleted 的订单或聊天记录, 文件大小是 4096 的整数倍]
difficulty: medium
source: "SQLite 官方文件格式文档 / Forensic Focus 关于 freelist 与 WAL 的取证文章"
tools: [python, sqlite3, sqlite-recover, 010editor, strings, walparse]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.db` / `.sqlite` / `.sqlite3`，或**无扩展名**但 `file` 识别为 `SQLite 3.x database`。
- 同目录出现 `xxx-wal`、`xxx-shm`、`xxx-journal`。
- `sqlite3 db "select count(*) from t"` 的结果与题目描述的数据量对不上。
- 题目问"被删除的用户""已下架的记录""过去七天的聊天"。
- 十六进制里看到成片 `00` 的空页，以及可读的 `CREATE TABLE` 字符串。
- 题目给了一个"最后一次正常备份"做对比，要求找差异。

## 二、原理

**SQLite 文件 = 100 字节文件头 + 若干页（默认 4096 字节）。**

- 页 1 是 `sqlite_master`（含表结构 SQL）。
- 每张表有 `rootpage`，B-tree 内部页与叶子页组成索引。
- **freelist**：文件头偏移 32 是 `first freelist trunk page`，偏移 36 是 freelist 页总数。被 `DELETE` 释放的页进入 freelist，**页内容不会被清零**，所以旧记录仍可被 ASCII 扫描捡回。
- **freeblock**：页内部的空洞由 unallocated 区的 freelist 管理，碎片化的记录删除后更难恢复。
- **WAL**：写前日志（默认 4096 字节一个帧），格式为 32 字节页头 + 24 字节帧头 + 页数据。**WAL 里保存的是"新版本页"**，如果 WAL 未被 checkpoint，那么数据库主体是旧状态、WAL 是最新状态。反过来，把 WAL 回放可以拿到被"撤销"的旧数据。
- **`-journal`（rollback journal）**：存的是"修改前的原页镜像"，撤销未提交事务时会用，是**最好的未删除数据来源**。
- **记录格式**：varint 头部 + serial types + 值，字符串通常就是连续 UTF-8，因此 `strings` 往往直接可见。

## 三、操作步骤

1. **先备份三件套**：`db`、`db-wal`、`db-journal`（缺一不可，只拷 db 会丢最新数据）。
2. **只读打开**：`sqlite3 'file:db?mode=ro&immutable=1'`，避免触发 checkpoint 改写 WAL。
3. **看 schema 与计数**：`SELECT name, type, sql FROM sqlite_master;`。
4. **回放 WAL**：把 `-wal` 与 db 一起放在同目录，用正常方式打开，SQLite 会自动恢复；或用 `sqlite3 db ".recover"` 导出所有可解析内容。
5. **扫 freelist**：用脚本读取文件头里的 freelist 页码，逐页 dump ASCII/UTF-8。
6. **全文件 strings**：`strings -n 6 db | grep -iE 'flag|@|http'`。
7. **carve 记录**：按 SQLite 记录格式解析出完整行。

## 四、命令 / 脚本

```bash
# 只读、不触发 checkpoint
sqlite3 'file:target.db?immutable=1' "SELECT type, name, sql FROM sqlite_master;"
sqlite3 'file:target.db?immutable=1' "PRAGMA freelist_count;"
# 官方 .recover（3.29+）
sqlite3 target.db ".recover" | sqlite3 recovered.db
# WAL 里有什么
python -c "
import glob
for f in glob.glob('target.db*'):
    print(f, open(f,'rb').read()[:16])
"
# 直接扫字符串
strings -n 6 target.db | sort -u | head -50
```

```python
#!/usr/bin/env python3
# SQLite freelist 页 dump：找出被删除但仍残留的页
import struct, sys

def dump_freelist(path):
    d = open(path, 'rb').read()
    assert d[:16] == b'SQLite format 3\x00', 'not sqlite3'
    page_size = struct.unpack('>H', d[16:18])[0] or 65536
    first, count = struct.unpack('>II', d[32:40])
    print('page_size=%d freelist_first=%d freelist_count=%d'
          % (page_size, first, count))
    p = first
    seen = set()
    while p and p not in seen:
        seen.add(p)
        off = (p - 1) * page_size
        trunk = d[off:off + page_size]
        n = struct.unpack('>I', trunk[4:8])[0]
        leaves = struct.unpack('>' + 'I' * n, trunk[8:8 + 4 * n])
        print('trunk page %d -> %d leaf pages: %s' % (p, n, list(leaves)))
        print('   trunk 残留:', trunk[8 + 4*n:8 + 4*n + 120])
        for lf in leaves:
            o = (lf - 1) * page_size
            body = d[o:o + page_size]
            print('   leaf %d 残留: %r' % (lf, body[:160]))
        p = struct.unpack('>I', trunk[0:4])[0]

if __name__ == '__main__':
    dump_freelist(sys.argv[1])
```

```python
#!/usr/bin/env python3
# SQLite 记录格式解析（叶子页 cell）——从 B-tree 页里直接抠记录
def read_varint(b, i):
    v = 0
    for k in range(9):
        c = b[i + k]
        if k == 8:
            return (v << 8) | c, i + 9
        v = (v << 7) | (c & 0x7f)
        if not c & 0x80:
            return v, i + k + 1
    raise ValueError

def parse_record(b, off, end):
    hdr_len, p = read_varint(b, off)
    hs, types = p, []
    while p < off + hdr_len:
        t, p = read_varint(b, p)
        types.append(t)
    p = off + hdr_len
    vals = []
    for t in types:
        if t == 0: vals.append(None)
        elif 1 <= t <= 6:
            nbytes = [0, 1, 2, 3, 4, 6, 8][t]
            vals.append(int.from_bytes(b[p:p + nbytes], 'big', signed=True)); p += nbytes
        elif t == 7:
            import struct; vals.append(struct.unpack('>d', b[p:p + 8])[0]); p += 8
        elif t == 8: vals.append(0); p += 0
        elif t == 9: vals.append(1); p += 0
        else:
            n = (t - 12) // 2 if t % 2 == 0 else (t - 13) // 2
            chunk = b[p:p + n]; p += n
            vals.append(chunk.decode('utf-8', 'replace') if t % 2 else chunk.hex())
    return vals
```

## 五、常见坑 / 变体

- **只拷了 db 没拷 wal**：最常见失误。`cp target.db* ./` 一起拷，否则最新数据全丢。
- **一打开就 checkpoint**：用只读 URI 加 `immutable=1`，否则 SQLite 会把 WAL 合并进 db 并删除它，取证原地被破坏。
- **页大小不是 4096**：从文件头偏移 16 读，`1` 表示 65536。
- **`secure_delete=PRAGMA` 开启时**：删除的页会被 0 覆盖，freelist 里什么都没有，只能靠 WAL/journal。
- **`VACUUM` 过**：数据库被重写，旧数据基本无望，改用文件系统层（unallocated space）恢复。
- **记录解析 off-by-one**：serial type 12/13 起的字符串长度 = `(t-12)/2` 或 `(t-13)/2`，很多实现在这里错位。
- **变体**：MySQL InnoDB `.ibd`（page 16 开始，需工具）、LevelDB（Chrome 的 `Local Storage`）、Realm/VS Code state。

## 六、参考来源

- [SQLite 官方文件格式文档（freelist 与 B-tree 页结构）](https://github.com/sqlite/sqlite)
- [Forensic Focus：SQLite Free Lists、WAL、Unallocated Space 与 Carving](https://www.forensicfocus.com/articles/forensic-analysis-of-sqlite-databases-free-lists-write-ahead-log-unallocated-space-and-carving/)
- [SQLite 官方的 .recover 命令说明](https://github.com/sqlite/sqlite)
- [WAL 模式与 checkpoint 机制（官方文档）](https://www.sqlite.org/fileformat2.html#wal)
- [恢复已删除 SQLite 记录的实践说明](https://elusivedata.io/nb/recover-deleted-sqlite-records-sqlite-database-recovery/)
