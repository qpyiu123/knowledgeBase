---
title: 图像地理定位进阶（卫星图比对、街景与超分辨率线索）
category: osint
tags: [geolocation, satellite, street-view, overpass, suncalc, geoguessr]
signals: [给了一张航拍图或者卫星截图要求定位, 图片来自某个地图软件的截图有明显缩放按钮, 需要根据阴影方向推断太阳方位和时间, 图里有铁路道口或者特殊路牌, 题目要求精确到街道名或者经纬度小数点后三位, 图片是街景截图但被模糊了车牌]
difficulty: hard
source: "Geoguessr 社区教程 / Overpass API 文档 / SunCalc 太阳位置计算 / 公开 OSINT 定位方法论"
tools: [python, overpass-turbo, suncalc, google-maps, yandex-maps, baidu-map, wikimapia]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是一张俯视/卫星视角的图，带地图水印或缩放控件。
- 街景截图：视角是驾驶员高度，有路面、标线、建筑。
- 题目问"这是哪个城市/哪条街/哪个坐标"。
- 图中有**明显的阴影**，可用于推算太阳方位角。
- 有文字只露出片段（路牌、店招、广告），属于强线索。
- 需要"精确坐标"，说明不是大致国家而是具体地点。

## 二、原理

**地理定位的三层证据链：**

| 层级 | 证据 | 可靠度 |
| --- | --- | --- |
| 宏观 | 气候带（植被、屋顶颜色、车牌样式）、文字语种、道路标线颜色 | 中（缩小到国家/地区） |
| 中观 | 地标建筑、桥梁形状、山脉轮廓、河流走向 | 高（缩小到城市） |
| 微观 | 街道布局与卫星图比对、门牌号、店铺名、电线杆样式 | 极高（锁定坐标） |

**太阳阴影法的物理基础**：已知时间（照片 EXIF 或题面给出）→ 用 SunCalc 算该地点的太阳方位角与高度角 → 阴影方向必须与之一致；反过来，若已知时间和阴影方向，可以反推纬度区间。

**卫星图比对**：用 OpenStreetMap/Overpass 按"道路拓扑特征"查询候选（如"三岔路口 + 铁路 + 湖泊"），再用卫星底图逐一对齐。

## 三、操作步骤

1. **读 EXIF**：`exiftool -a -u -g1`，看 GPS、拍摄时间、设备型号。
2. **语种与文字**：截图里的任何文字先 OCR 或人眼识别语种。
3. **找独特地形**：海岸线、河流弯曲、湖泊形状、山头轮廓。
4. **阴影推断**：量阴影方向与长度，配合 SunCalc 缩小纬度与时间窗。
5. **卫星/街景比对**：用 Google Street View / Bing Streetside / Yandex 全景，先找街区，再沿街走。
6. **Overpass 反查**：用道路标签（`highway=crossing`、`railway=level_crossing`）在候选城市内搜索匹配点。
7. **精确化**：用 Overpass 或地图坐标工具读出经纬度，验证题面要求的精度。

## 四、命令 / 脚本

```bash
# 元数据与文本
exiftool -a -u -g1 photo.jpg | grep -iE 'gps|date|make|model'
tesseract photo.jpg stdout -l chi_sim+eng 2>/dev/null | head
```

```python
#!/usr/bin/env python3
# 用阴影方向 + 已知时间反推可能的纬度（太阳方位角近似）
import math, datetime

def solar_declination(doy):
    return 23.44 * math.sin(math.radians(360 / 365 * (doy - 81)))

def hour_angle_deg(local_hour, lon, utc_off):
    """时角（度）：正午为 0，下午为正"""
    utc_h = local_hour - utc_off
    return (utc_h - 12) * 15 + (lon % 15 - 15 / 2)

def azimuth_az(decl, hour_angle, lat):
    d, h, p = map(math.radians, (decl, hour_angle, lat))
    az = math.atan2(math.sin(h), math.cos(h) * math.sin(p) - math.tan(d) * math.cos(p))
    return (math.degrees(az) + 180) % 360      # 0=北, 90=东

def invert(obs_az, date, local_hour, lon, utc_off):
    doy = date.timetuple().tm_yday
    decl = solar_declination(doy)
    ha = hour_angle_deg(local_hour, lon, utc_off)
    hits = []
    for lat10 in range(-900, 901, 5):
        lat = lat10 / 10.0
        if abs(azimuth_az(decl, ha, lat) - obs_az) < 2:
            hits.append(lat)
    return hits

if __name__ == '__main__':
    dates = datetime.date(2023, 7, 1)
    print('候选纬度区间:', invert(obs_az=125.0, date=dates, local_hour=10.5,
                                  lon=116.4, utc_off=8))
```

```bash
# Overpass：在候选城市内找"三岔路口 + 铁路道口"的组合
cat > q.overpass <<'EOF'
[out:json][timeout:60];
area["name:en"="Harbin"]->.a;
(
  node["railway"="level_crossing"](area.a);
);
out body;
EOF
curl -s -d @q.overpass https://overpass-api.de/api/interpreter | jq '.elements | length'
```

```python
#!/usr/bin/env python3
# 批量计算候选点的太阳位置，用于排除不可能的纬度
import math

def sun_position(lat, lon, when_utc):
    """返回 (高度角, 方位角)，简化公式，精度约 1 度"""
    import datetime
    n = when_utc.timetuple().tm_yday
    decl = 23.44 * math.sin(math.radians(360 / 365 * (n - 81)))
    hour = when_utc.hour + when_utc.minute / 60 + lon / 15
    ha = math.radians((hour - 12) * 15)
    d, p = math.radians(decl), math.radians(lat)
    alt = math.asin(math.sin(p) * math.sin(d) + math.cos(p) * math.cos(d) * math.cos(ha))
    az = math.atan2(math.sin(ha), math.cos(ha) * math.sin(p) - math.tan(d) * math.cos(p))
    return math.degrees(alt), (math.degrees(az) + 180) % 360

if __name__ == '__main__':
    import datetime
    t = datetime.datetime(2023, 7, 1, 2, 30)   # UTC
    for lat in (20, 30, 40, 50):
        print('lat %d -> alt/az %s' % (lat, sun_position(lat, 116.4, t)))
```

## 五、常见坑 / 变体

- **截图的缩放级别**：卫星图截图的每条道路宽度不同，用"建筑与道路的比例"校准 pixel/m。
- **地图投影**：高纬度地区的经纬网格在 Web Mercator 下会被拉伸，直接按像素算距离会偏。
- **停留在城市差异**：中国、俄罗斯、印度、巴西的卫星底图更新时间不同，同一地方不同年份差别很大。
- **街景的"车顶相机"位置**：Google 街景的采集车在右侧车道，视角高度约 2.5m，这决定了视野里的地平线位置。
- **阴影法的失效条件**：正午（阴影过短）、阴天（无阴影）、有遮挡时不可用。
- **时限与精度**：题目要"小数点后三位"意味着必须在卫星图上精确对齐路口，误差不能超过几米。
- **变体**：Geoguessr 特有的"元技巧"（车牌格式、道路标记颜色、电线杆材质）、KartaView/Mapillary 的替代街景。

## 六、参考来源

- [Overpass Turbo：按 OSM 标签查询地物的在线工具](https://overpass-turbo.eu/)
- [Overpass API 官方文档（查询语法）](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [SunCalc：太阳位置与阴影计算](https://www.suncalc.org/)
- [EarthGuessr vs GeoGuessr：卫星图与街景的定位思路对比](https://www.earthguessr.com/blog/geoguessr-vs-earthguessr-comparison)
- [Google 街景官方帮助（覆盖范围与拍摄方法）](https://support.google.com/maps/answer/3093484)
