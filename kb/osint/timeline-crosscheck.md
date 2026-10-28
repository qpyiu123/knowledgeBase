---
title: 时间线交叉验证（多源信息配置与矛盾检测）
category: osint
tags: [timeline, cross-validation, timestamps, consistency, evidence]
signals: [题目给出了多张照片和几段对话要求判断先后, 需要还原某个人在某个时间段的行踪, 信息之间有时间冲突需要判断哪条是伪造的, 题目给了时区不同地区的截图, 要求证明某张截图不可能在所述时间拍摄, 给了多个来源的天气或者航班记录]
difficulty: hard
source: "OSINT 时间线方法论公开资料 / Bellingcat 的调查流程 / 元数据与时间戳一致性研究"
tools: [python, exiftool, pandas, suncalc, timezonefinder, jq]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是多张截图 + 一段聊天记录，要求"还原事件顺序"。
- 题目问"哪一条信息是伪造的"或"哪张图不可能在那个时间拍"。
- 材料里有不同时区的截图（`UTC`、`+0800`、`PST` 混用）。
- 需要结合天气、航班、营业时间等外部事实判断可行性。
- 题面给出"某人在 3 天内做了 X 件事"。
- 要求输出"时间线表格"作为答案。

## 二、原理

**交叉验证 = 让多个独立来源对同一个事实做约束，找到唯一自洽解。**

常见约束维度：

| 维度 | 约束方式 |
| --- | --- |
| 物理可行性 | 两地之间的最短交通时间 vs 声称的时间差 |
| 光照 | 阴影方向/长度 vs SunCalc 给出的太阳位置 |
| 天气 | 截图里的晴雨 vs 气象记录 |
| 元数据 | EXIF 的 `DateTimeOriginal` vs 文件系统 `mtime` vs 聊天发送时间 |
| 时区 | 截图的系统时区 vs 消息内容的"现在几点" |
| 语言/法律 | 营业时间、法定节假日 |
| 数字指纹 | 同一张图的压缩痕迹、尺寸、水印版本 |

**矛盾检测的关键**：单条证据永远不可信，**两条独立证据互相矛盾时，说明至少一条被修改**；矛盾点本身往往就是题目的 flag。

## 三、操作步骤

1. **建立事件表**：每条信息一行，字段 `时间(原始)`、`时区`、`来源`、`内容`、`可验证性`。
2. **全部转 UTC**：统一后再排序，避免"表面顺序"误导。
3. **逐条打标签**：`事实`（可外部验证）/ `声称`（当事人说的）/ `推断`（你的推理）。
4. **跑约束检查**：距离-时间、光照、天气、营业时间。
5. **标记矛盾点**：把冲突的两条摆在一起，判断哪条更可信。
6. **输出结论**：给出最自洽的时间线 + 指出伪造项。

## 四、命令 / 脚本

```bash
# 元数据时间线
exiftool -a -u -g1 -time:all *.jpg | grep -E 'DateTime|File Modification'
# 文件系统的 mtime（可能被复制修改过）
stat -c '%y %n' *.jpg
```

```python
#!/usr/bin/env python3
# 多源时间线合并 + 矛盾检测
import pandas as pd, itertools

def to_utc(df):
    df['utc'] = pd.to_datetime(df['time'], utc=True)
    return df

def travel_feasible(t1, c1, t2, c2, km_per_h=60, min_gap_min=20):
    """粗略判断两地之间的最短耗时是否与声称的时间差矛盾"""
    from math import radians, sin, cos, asin, sqrt
    def hav(a, b):
        la1, lo1, la2, lo2 = map(radians, [a[0], a[1], b[0], b[1]])
        h = sin((la2-la1)/2)**2 + cos(la1)*cos(la2)*sin((lo2-lo1)/2)**2
        return 2 * 6371 * asin(sqrt(h))
    dist = hav(c1, c2)
    need_min = dist / km_per_h * 60 + min_gap_min
    gap_min = (t2 - t1).total_seconds() / 60
    return gap_min >= need_min, dist, need_min, gap_min

df = pd.DataFrame([
    {'time': '2024-03-01T10:00:00+08:00', 'src': 'photo1', 'place': (31.2304, 121.4737)},  # 上海
    {'time': '2024-03-01T11:30:00+08:00', 'src': 'photo2', 'place': (39.9042, 116.4074)},  # 北京
    {'time': '2024-03-01T13:00:00+08:00', 'src': 'chat',   'place': (31.2304, 121.4737)},
])
df = to_utc(df).sort_values('utc').reset_index(drop=True)

for (i, a), (j, b) in itertools.combinations(df.iterrows(), 2):
    ok, d, need, gap = travel_feasible(a['utc'], a['place'], b['utc'], b['place'])
    print('%s -> %s  距离 %.0fkm 需要 %.0fmin 实际 %.0fmin %s'
          % (a['src'], b['src'], d, need, gap, 'OK' if ok else '!! 矛盾'))
```

```python
#!/usr/bin/env python3
# 光照检查：同样的影子在给定时间是否可能出现
import math, datetime

def sun_alt_az(lat, lon, t_utc):
    n = t_utc.timetuple().tm_yday
    decl = 23.44 * math.sin(math.radians(360 / 365 * (n - 81)))
    hour = t_utc.hour + t_utc.minute / 60 + lon / 15
    ha = math.radians((hour - 12) * 15)
    p, d = math.radians(lat), math.radians(decl)
    alt = math.asin(math.sin(p) * math.sin(d) + math.cos(p) * math.cos(d) * math.cos(ha))
    az = math.atan2(math.sin(ha), math.cos(ha) * math.sin(p) - math.tan(d) * math.cos(p))
    return math.degrees(alt), (math.degrees(az) + 180) % 360

def shadow_len_ratio(alt):
    return None if alt <= 0 else 1 / math.tan(math.radians(alt))

if __name__ == '__main__':
    for h in range(6, 19, 2):
        t = datetime.datetime(2024, 3, 1, h - 8, 0)   # 北京时间 -> UTC
        alt, az = sun_alt_az(31.23, 121.47, t)
        print('%02d:00 alt=%.1f az=%.0f 影长比=%s' % (h, alt, az,
              '无' if alt <= 0 else '%.2f' % shadow_len_ratio(alt)))
```

```bash
# 时区换算一次到位
python -c "
import datetime, zoneinfo
t = datetime.datetime(2024,3,1,10,0,tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
print(t.astimezone(datetime.timezone.utc))
print(t.astimezone(zoneinfo.ZoneInfo('America/Los_Angeles')))
"
```

## 五、常见坑 / 变体

- **"看起来一致"不等于一致**：伪造者会同步大部分时间戳，但**跨源矛盾**（如航班记录 vs 照片）最难伪造。
- **夏令时**：美国/欧洲的 DST 会让"同一时刻"差 1 小时，换算前先查当年 DST 起止。
- **文件 mtime 不可信**：复制、下载都会重置，只有 EXIF 的 `DateTimeOriginal` 有参考价值（也可被改）。
- **聊天记录截图**：不同 App 的"已读/未读"、状态栏时间、电量都是隐藏校验点。
- **交通时间不能只看直线**：实际航班/火车班次才是硬约束。
- **结论表述**：写"在某假设下最可能"，并列出被排除的项，比直接下结论更严谨。
- **变体**：结合航班数据的航班追踪、结合卫星图的建筑变化（Google Earth 历史影像）、结合网络日志的登录记录。

## 六、参考来源

- [SunCalc：任意时间地点的太阳方位与高度](https://www.suncalc.org/)
- [Bellingcat：开源调查中的时间线验证方法](https://www.bellingcat.com/resources/how-tos/)
- [timezonefinder：从经纬度推断时区](https://github.com/jannikmi/timezonefinder)
- [pandas 时间序列与时区处理](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [exiftool 的 -time:all 与元数据时间字段说明](https://exiftool.org/TagNames/EXIF.html)
