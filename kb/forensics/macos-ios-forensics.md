---
title: macOS / iOS 取证要点
category: forensics
tags: [macos, ios, itunes备份, keychain, 统一日志, apfs]
signals: [附件是 dmg 或 sparseimage, 附件是 iphone 备份目录, 题目要求看 mac 上的记录, 需要解 keychain, 需要对 plist 分析]
difficulty: hard
source: "Apple 平台安全指南 / macOS 统一日志文档 / iOS 备份格式研究文献"
tools: [plutil, sqlite3, mac_apt, iLEAPP, keychain-dumper, apfs-fuse, log show]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.dmg`、`.sparseimage`、`.apfs` 或 `hdiutil` 产物。
- 附件目录形如 `MobileSync/Backup/<UDID>/`，里面有 `Manifest.plist`、`Manifest.db`。
- 题目问「用户在 Mac 上干了什么」「找到 Safari 历史或钥匙串密码」。
- 附件里有 `.plist`、`.logarchive`、`knowledgeC.db`、`TCC.db`。

## 二、原理

**macOS**：

- 文件系统是 **APFS**（容器 + 卷 + 快照），可用 `apfs-fuse` 或 macOS 的 `hdiutil attach` 挂载。
- 大量数据在 SQLite 与 plist 里：Safari 历史（`History.db`）、Spotlight、**统一日志（`*.logarchive`）**、**TCC 权限**（`TCC.db`）、`knowledgeC.db`（应用使用时长）。
- **keychain（`login.keychain-db`）** 用用户登录密码加密，能拿到密码或已解锁会话时才能导出。

**iOS**：

- **iTunes/Finder 备份**：`Manifest.db` 记录「文件 ID → 域 → 相对路径」，文件名被**哈希**（SHA1 全 40 位做文件名，前两位做目录）。
- **加密备份**：`Manifest.plist` 里 `IsEncrypted=true`，密钥由备份密码派生，需要密码才能解。
- **App 数据**：`AppDomain-*`、`HomeDomain`（含短信 `Library/SMS/sms.db`、通话记录、通讯录、日历）。
- **越狱设备**：可直接取 `/private/var/mobile/Library/`。

## 三、操作步骤

1. **判容器**：`file img` → `dmg`/`sparseimage`/APFS/HFS+ 走不同路径。
2. **挂载只读**：macOS 用 `hdiutil attach -readonly -noverify`；Linux 用 `apfs-fuse`/`hfsplus`。
3. **plist**：`plutil -p` 转文本，`plutil -convert xml1` 便于 grep。
4. **SQLite**：`sqlite3 <db> '.tables'` 然后查关键表。
5. **备份分析**：用 `iLEAPP` 一键解析；或手工查 `Manifest.db`。
6. **加密备份**：用 `mvt` 或 `iOSbackup` 这类库解密后分析。

## 四、命令/脚本

### 挂载镜像

```bash
# macOS 本机
hdiutil attach -readonly -noverify disk.dmg -mountpoint /Volumes/ev
hdiutil info
hdiutil detach /Volumes/ev

# Linux 上挂 APFS / HFS+
sudo apt install -y apfs-fuse hfsplus hfsprogs
sudo apfs-fuse /dev/sdb2 /mnt/apfs -o ro,allow_other
sudo mount -t hfsplus -o ro,loop,offset=$((2048*512)) disk.img /mnt/hfs

# sparseimage / dmg 是 macOS 专有：Linux 先转 raw
dmg2img disk.dmg disk.img
```

### plist 解析

```bash
plutil -p Info.plist | head -30
plutil -convert xml1 -o - Info.plist | grep -A2 -i 'key'
# 二进制 plist 在 Linux 上用 python
python3 -c "
import plistlib
print(plistlib.load(open('Info.plist','rb')))"
# 批量转文本后全盘 grep
find . -name '*.plist' -exec plutil -convert xml1 {} \; 2>/dev/null
grep -ril 'flag' --include='*.plist' .
```

### 关键 SQLite 位置

```bash
sqlite3 ~/Library/Safari/History.db 'select url, visit_count from history_items order by visit_count desc limit 10;'
sqlite3 ~/Library/Application\ Support/Google/Chrome/Default/History 'select url,title from urls limit 10;'
sqlite3 ~/Library/Application\ Support/Knowledge/knowledgeC.db '.tables'
sqlite3 /Library/Application\ Support/com.apple.TCC/TCC.db 'select client,service from access;'
```

```python
#!/usr/bin/env python3
# ios_manifest.py —— 解析 iOS 备份的 Manifest.db，按 domain 列出文件
import sqlite3, sys
db = sys.argv[1] if len(sys.argv) > 1 else 'Manifest.db'
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("select fileID, domain, relativePath, flags from Files limit 20")
for fid, dom, path, flags in cur:
    print(f'{dom:35s} {(path or "")[:55]:55s} {fid[:8]} flags={flags}')
print('--- domains ---')
for (dom,) in con.execute("select distinct domain from Files order by 1"):
    print(dom)
```

```bash
python ios_manifest.py Manifest.db | grep -iE 'HomeDomain|AppDomain'
# 还原某个文件：fileID 前 2 位做目录，全名做文件名
python3 -c "
import sqlite3, shutil
c = sqlite3.connect('Manifest.db')
fid = c.execute(\"select fileID from Files where relativePath='Library/SMS/sms.db'\").fetchone()[0]
shutil.copy(f'{fid[:2]}/{fid}', 'sms.db')
print('saved sms.db')"
sqlite3 sms.db 'select text from message limit 10;'
```

### 统一日志（logarchive）

```bash
# macOS 本机直接查
log show --archive system.logarchive --last 1h --predicate 'process == "sshd"'
log show --archive system.logarchive --info --debug | grep -i 'flag' | head
# Linux 侧用 macos-unifiedlogs 解析二进制 tracev3
pip install macos-unifiedlogs
python3 -c "
from macos_unifiedlogs import unified_log_parser
for e in unified_log_parser.parse_file('system.logarchive/Persist/0000000000000001.tracev3')[:3]:
    print(e)"
```

### keychain

```bash
# 只在自己授权的设备上做
security dump-keychain -d login.keychain-db > kc.txt
security find-generic-password -s 'Wi-Fi' -w
# 加密 keychain + 知道登录口令时离线爆破
keychain2john login.keychain-db > kc.hash && john kc.hash --wordlist=rockyou.txt
```

### APFS 快照与时间线

```bash
tmutil listlocalsnapshots /
diskutil apfs listSnapshots /dev/disk3s1
mount_apfs -s com.apple.TimeMachine.2026-03-01-100000.local /dev/disk3s1 /Volumes/snap
# 对比两个快照中同一文件
diff <(ls /Volumes/snap/Documents) <(ls ~/Documents)
```

## 五、常见坑 / 变体

- **加密备份**：没有备份密码时 `Manifest.db` 也打不开；先看 `Manifest.plist` 里的 `IsEncrypted`。
- **文件名哈希**：iOS 备份里 `find -name '*flag*'` 找不到东西，必须查 `Manifest.db` 映射。
- **APFS 多卷**：`diskutil apfs list` 看卷角色，用户数据在 **Data** 卷（不是 System 卷）。
- **DMG 加密**：`hdiutil attach -stdinpass`，密码可能在题面。
- **Linux 上解析 plist**：`plistlib` 原生支持二进制 plist。
- **SQLite WAL**：`sms.db-wal` 里有未落盘消息；先拷贝到可写目录再打开会自动合并。
- **TCC.db 能看权限授予历史**，常被用作"是否访问过某目录"的旁证。

## 六、参考来源

- [Apple 平台安全指南（数据保护与钥匙串）](https://support.apple.com/guide/security/welcome/web)
- [Apple 统一日志官方文档（Logger / log show）](https://developer.apple.com/documentation/os/logging)
- [plutil 用法参考](https://ss64.com/mac/plutil.html)
- [mac_apt - macOS 取证套件](https://github.com/ydkhatri/mac_apt)
- [MVT - Mobile Verification Toolkit（iOS 备份解析）](https://github.com/mvt-project/mvt)
- [iLEAPP - iOS 本地端取证分析工具](https://github.com/abrignoni/iLEAPP)
