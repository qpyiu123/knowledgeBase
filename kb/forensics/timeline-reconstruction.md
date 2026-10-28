---
title: 日志时间线重建（plaso / timesketch / 多源时间归一）
category: forensics
tags: [plaso, log2timeline, timesketch, timeline, super-timeline, csv]
signals: [题目要求还原某个时间点到底发生了什么, 给了多个来源的日志需要合并成一份时间线, 日志时间戳有 utc 和本地时间混用, 附件里有 evtx 和 json 和 csv 多种格式, 题目问事件 A 和事件 B 谁先发生, 给了很大的日志集但是只有一个关键时间段, 需要按主机分组统计活动频次]
difficulty: medium
source: "Plaso 官方文档 / Timesketch 官方文档 / Log2Timeline 项目"
tools: [python, plaso, log2timeline, timesketch, pandas, jq, mactime]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件含 `.evtx`、`syslog`、`access.log`、`journal`、`.jsonl`、`$MFT` 等多种格式。
- 题面问"攻击者第一次登录是什么时候""在 14:32 前后发生了什么"。
- 日志时间戳一栏有 `+0800`、`Z`、`UTC` 混着出现。
- 数据量几个 GB，单个文件能 grep 但整体拼不起来。
- 需要给出"事件序列"或"最短时间间隔"作为答案。
- 题目给了多个时区不同机器的日志，要求统一到同一时间轴。

## 二、原理

**时间线重建 = 归一化 + 合并 + 排序 + 过滤。**

- **归一化**：所有时间戳转成 UTC + 明确格式（推荐 ISO8601）。常见的坑是"本地时间误当 UTC"——差 8 小时会把因果链颠倒。
- **plaso（log2timeline）**：把 200+ 种格式（evtx、MFT、浏览器历史、注册表、syslog、pcap 提取）统一成 **storage file**（SQLite），每个事件含 `timestamp`（UTC）、`source`、`type`、`message`、`hostname`。
- **timesketch**：plaso 或 csv 的 Web 前端，支持全文检索、直方图、多条柱状对比、协作标注。
- **精简路线**：只有几种格式时，用 pandas 把各源的 `(时间, 主机, 来源, 描述)` 合并排序，往往比装 plaso 快。

## 三、操作步骤

1. **清单**：`file` 所有附件，按格式分组（evtx / 文本 / 结构化）。
2. **确认时区**：看日志头、系统区域设置、时间戳与相邻事件的一致性。
3. **小规模 → pandas**：每源写一个解析器，统一列名后 `concat` + `sort_values`。
4. **大规模 → plaso**：`log2timeline.py --storage-file out.plaso <证据目录>`，再 `psort.py -w tl.csv out.plaso`。
5. **过滤**：按时间窗、主机、关键字筛选，导出到 timesketch 可视化。
6. **结论化**：输出"关键事件表"，并把推导链（A 导致 B）写清楚。

## 四、命令 / 脚本

```bash
# plaso 全流程
pip install plaso
log2timeline.py --status_view window --storage-file case.plaso evidence_dir/
psort.py -o L2tcsv -w timeline.csv case.plaso "date > '2024-03-01 00:00:00' and date < '2024-03-02 00:00:00'"
psort.py case.plaso "message contains 'flag'"
# 只要特定来源
psort.py case.plaso -w evtx.csv --source "EVT"
# mactime（TSK 自带，轻量）
fls -m / -o 63 -r disk.dd > bodyfile.txt
mactime -b bodyfile.txt -d -z UTC 2024-03-01..2024-03-02 > timeline.csv
# timesketch（docker）
docker run -d -p 80:80 -p 5000:5000 --name timesketch us-docker.pkg.dev/osdfir-registry/timesketch/timesketch
```

```python
#!/usr/bin/env python3
# 多源日志归一化合并（pandas 路线）
import pandas as pd, json, datetime, glob

def iso(s):
    return pd.to_datetime(s, utc=True)

rows = []
# 1) syslog（假设 "Mar  1 14:32:10" 无时区，按 +0800 本地）
for line in open('syslog', encoding='utf-8', errors='replace'):
    p = line.split(None, 5)
    if len(p) < 6:
        continue
    ts = pd.to_datetime('2024 ' + ' '.join(p[:3]), utc=False) - pd.Timedelta(hours=8)
    rows.append({'time': ts.tz_localize('UTC'), 'host': p[3], 'src': 'syslog', 'msg': p[5].strip()})
# 2) JSONL（ISO8601 UTC）
for f in glob.glob('*.jsonl'):
    for line in open(f, encoding='utf-8'):
        j = json.loads(line)
        rows.append({'time': iso(j['eventTime']), 'host': j.get('host', 'app'),
                     'src': f, 'msg': json.dumps(j.get('detail', j), ensure_ascii=False)[:300]})
# 3) Apache access log
import re
pat = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3})')
for line in open('access.log', encoding='utf-8', errors='replace'):
    m = pat.match(line)
    if m:
        ts = pd.to_datetime(m.group(2), format='%d/%b/%Y:%H:%M:%S %z')
        rows.append({'time': ts.tz_convert('UTC'), 'host': 'web', 'src': 'apache',
                     'msg': '%s %s %s' % (m.group(1), m.group(3), m.group(4))})

df = pd.DataFrame(rows).sort_values('time')
df.to_csv('merged.csv', index=False)
print(df.head(30).to_string())
print('总事件', len(df), '范围', df.time.min(), '->', df.time.max())
```

```bash
# 快速"谁先发生"对比
pandas 版：
python -c "
import pandas as pd
df = pd.read_csv('merged.csv', parse_dates=['time'])
print(df[df.msg.str.contains('login|auth|flag', case=False)].head(20))
"
```

## 五、常见坑 / 变体

- **时区错 8 小时最致命**：Windows 事件日志的 `SystemTime` 是 UTC，但 `TimeCreated` 的显示字段可能带本地偏移；先统一验证一条已知事件。
- **NTP 漂移**：不同主机的时钟可能有秒级偏差，因果判断时留 1~2 分钟容差。
- **pandas 的 tz-aware 比较**：naive 与 aware 混拼直接报错，全部 `tz_localize('UTC')`。
- **plaso 存储文件很大**：几百万事件后 `psort` 要几分钟，先按时间窗过滤再导出。
- **重复事件**：同一事件在 syslog 与 app log 各记一份，去重要按 `(时间, host, msg)`。
- **mactime 的时间窗**：`-d -z UTC` 加日期范围能显著降噪。
- **变体**：Windows `$UsnJrnl` + Prefetch + AmCache 联合排序（Windows 取证标准组合）；网络侧用 Zeek 的 `conn.log`/`http.log` 与端点日志对齐。

## 六、参考来源

- [Plaso 官方文档（log2timeline / psort 用法）](https://plaso.readthedocs.io/en/latest/)
- [Timesketch 官方站点与部署说明](https://timesketch.org/)
- [Working with log2timeline and Timesketch（实操视频）](https://www.youtube.com/watch?v=MuHOCdO0aSk)
- [Sleuth Kit mactime 手册](https://www.sleuthkit.org/sleuthkit/man/mactime.html)
- [pandas 时间序列与时区处理文档](https://pandas.pydata.org/docs/user_guide/timeseries.html)
