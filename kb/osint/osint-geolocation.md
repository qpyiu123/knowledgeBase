---
title: 地理定位技巧（阴影 / 路标 / 语言 / 星象）
category: osint
tags: [geolocation, geoguessr, 阴影, 太阳高度角, 路牌, 车牌]
signals: [题目给一张街景照片问在哪, 需要根据照片定位坐标, 照片有电线杆和路牌, 照片有云或太阳, 需要找经纬度写入 flag]
difficulty: medium
source: "CTF-Wiki 信息搜集技术 / GeoGuessr 官方站 / suncalc 太阳位置计算 / OpenStreetMap wiki"
tools: [google-maps, google-earth, suncalc, overpass-turbo, mapillary, wigle, geospy, google-lens]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件只有一张照片，题目问「这是哪里」「把经纬度写进 flag」。
- 格式形如 `flag{31.2304,121.4737}` 或 `flag{Location: Paris}`。
- 图片里有明显的人造物：车牌、路牌文字、广告牌、电线杆。
- 光照强烈，有可以判断"太阳方位"的阴影。

## 二、原理

定位的本质是**特征叠加收敛**：

1. **文字类（最强）**：路牌、店招、车牌格式、语言与文字系统、电话区号、海拔标识。直接反查即刻命中。
2. **自然类**：植被类型（棕榈/针叶/桉树）、地貌（红土/喀斯特/冰川）、天空（是否有云量、太阳高度）。
3. **人造制度类**：靠左/靠右行驶、车牌颜色、电线杆样式（木质/混凝土/日式带弧形）、邮箱样式、护栏颜色。
4. **天文类**：由**阴影方向 + 照片时间的 EXIF 时间**反推纬度与朝向——`suncalc` 给定经纬度可算出该时刻太阳方位角，与实际阴影夹角匹配的纬度就是候选纬度。太阳高度角给出纬度约束。
5. **反向收敛**：先用大致国家/城市缩小，再在 Google Maps/街景中逐街比对。

## 三、操作步骤

1. **读 EXIF**：`DateTimeOriginal`、`GPS`（如果有，直接结束）、`Make/Model`（相机型号 -> 国家分布）。
2. **文字识别**：`tesseract` 或直接肉眼，搜关键字（店名 + 城市）。
3. **判断国家**：语言/文字、车牌样式、行驶方向、license plate 颜色。
4. **找遮挡特征**：电线杆、消防栓、邮筒、交通标志形状（欧洲圆形 vs 北美方形）。
5. **太阳校验**：用 suncalc 反推纬度，排除无关纬度带。
6. **街景比对**：Google Street View / Mapillary / Bing Streetside 找同一视角。

## 四、命令/脚本

### 提取文字与元数据

```bash
exiftool -a -u -g1 photo.jpg | grep -iE 'date|gps|make|model|software'
tesseract photo.jpg - -l chi_sim+eng 2>/dev/null | head -30
# 只识别局部（裁出招牌区域）
magick photo.jpg -crop 400x200+100+300 crop.png && tesseract crop.png - -l eng
```

### 由阴影 + 时间反推纬度

```python
#!/usr/bin/env python3
# sun_reverse.py —— 给定 EXIF 时间与阴影方向，扫描纬度找最匹配解
# 需要：pillow (可选), 以及 pip install pysolar 或 astral
from astral import LocationInfo
from astral.sun import azimuth, elevation
from datetime import datetime, timezone
import sys

# 假设：照片在 UTC 时间 T 拍摄，阴影（物体指向的方向）约为 AZ_DEGREES 度
T = datetime(2026, 8, 15, 6, 30, tzinfo=timezone.utc)   # 来自 EXIF 的时间
SHADOW_DIR = 285.0        # 阴影指向（从物体看出去的方向，正北=0，顺时针）

def best_lat(lon_guess=0.0):
    cands = []
    for lat in range(-60, 61):
        loc = LocationInfo("x", "x", "UTC", lat, lon_guess)
        try:
            az = azimuth(loc.observer, T)
            el = elevation(loc.observer, T)
        except Exception:
            continue
        # 阴影方向 = 太阳方位 + 180
        diff = abs(((az + 180) % 360) - SHADOW_DIR)
        diff = min(diff, 360 - diff)
        cands.append((diff, lat, az, el))
    cands.sort()
    return cands[:5]

for d, lat, az, el in best_lat(116.0):
    print(f'lat={lat:4d}  diff={d:6.2f}  sun_az={az:6.2f}  sun_el={el:5.2f}')
```

```bash
pip install astral
python sun_reverse.py
# 找到 lat 后，再在 Google Maps 上沿该纬度线搜索文字特征
```

### 街景与地图交叉验证

```bash
# Google Earth 坐标格式（度分秒）与十进制互转
python -c "print(31 + 13/60 + 43.2/3600, 121 + 28/60 + 29.4/3600)"
# 地图直链
echo 'https://www.google.com/maps/place/31.2289,121.4748/@31.2289,121.4748,17z'
echo 'https://www.openstreetmap.org/#map=18/31.2289/121.4748'
# Overpass API 反查某区域内的特定 POI（路名/商店）
curl -s 'https://overpass-api.de/api/interpreter' --data-urlencode \
  'data=[out:json];node["name"~"火车站"](around:2000,31.2289,121.4748);out;' | head -c 600
```

### WiFi BSSID 反查（有 SSID/MAC 时）

```bash
# WiGLE 是公开的 WiFi 地理数据库
# https://wigle.net/search?ssid=YourSSID
curl -s 'https://wigle.net/api/v2/search?ssid=TARGET_SSID' \
  -H 'Accept: application/json' | head -c 400
```

### 快速排除的"特征表"

```
路牌：加拿大 / 美国（方形绿底）、欧洲（圆形限速）
车道：英国/日本/香港/印度/澳洲靠左
车牌：白底黑字（德/法/大陆部分）、黄底（英国后牌）、
     蓝底（欧盟侧条）、红字（临时牌）
电线杆：日本（弧形横担）、中国（直线十字）、欧洲常见双木杆
植被：桉树 -> 澳/南非/加州；棕榈 -> 热带；白桦 -> 高纬北方
建筑窗：德式内开/竖长窗；北欧深色木屋；地中海白墙瓷砖
```

## 五、常见坑 / 变体

- **EXIF 被清除**：微信/截图会清元数据，此时只能靠视觉特征。
- **太阳方位反推的误差**：需要照片时间**准确到分钟**，且要知道是上午/下午（阴影朝西=下午）。
- **镜像照片**：左右翻转会让"靠左/靠右行驶"判断彻底反掉，注意文字是否反写。
- **同一特征多国通用**：这样再多给一条约束（语言 + 植被），不要单靠一条下结论。
- **季节/时区**：南半球季节相反，EXIF 时间为 UTC 时注意换算。
- **CTF 常见区间**：经纬度常以 6 位小数写进 flag，答案通常是"著名地标"或"题目出题人学校附近"。

## 六、参考来源

- [CTF Wiki - 信息搜集技术](https://ctf-wiki.org/misc/recon/)
- [GeoGuessr 官方站（模式与地图练习）](https://www.geoguessr.com/)
- [SunCalc - 任意时间地点的太阳位置](https://www.suncalc.org/)
- [Astral - Python 太阳位置库](https://github.com/sffjunkie/astral)
- [Mapillary - 开源街景图库](https://www.mapillary.com/app/)
- [WiGLE - 全球 WiFi 位置数据库](https://wigle.net/)
- [Overpass Turbo - OSM 查询与可视化](https://overpass-turbo.eu/)
