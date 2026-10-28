---
title: 文档隐写（PDF 对象流 / docx、pptx 解压 / OLE）
category: misc
tags: [pdf, docx, pptx, xlsx, ole, 文档隐写]
signals: [附件是 pdf 或 docx, 文档打开后只有几行字, 文件体积偏大, pdf 里有多个 EOF, 文档里有隐藏文字或图片, 需要解压 docx 看结构]
difficulty: easy
source: "Aperi'Solve files & archives 分支 / Didier Stevens pdf-tools / OOXML 规范 / oletools 文档"
tools: [pdfid, pdf-parser, pdfdetach, pdftotext, qpdf, mutool, 7z, oletools, exiftool]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件是 `.pdf`，打开只显示一句话，但文件 3~10 MB。
- PDF 里有一段"看不见的文字"（白色字/白色背景）。
- 附件 `.docx`/`.pptx`/`.xlsx`，改后缀为 `.zip` 能解压——说明结构就是 ZIP。
- `strings` 在 PDF 里看到 `%%EOF` 出现两次以上。
- 文档属性（Creator/Title/Keywords）里有奇怪的字符串。
- 打开 PDF 提示"包含嵌入文件"或"被加密"。

## 二、原理

**PDF** 是对象流格式：`obj ... endobj`，页面的可见内容在 `Content Stream` 里（通常是 FlateDecode 压缩的 zlib）。常见藏法：

1. **额外对象/增量更新**：编辑过的 PDF 会追加新的 xref 和对象，旧版本内容仍在文件里，用 `pdfresurrect` 提取旧版本。
2. **不可见对象**：白色文字、0 号字体、页面外坐标，`pdftotext` 仍能提取。
3. **嵌入附件**：`/EmbeddedFile`（`pdfdetach`），或图片对象里套隐写图。
4. **图像流**：PDF 里的 XObject 图像用 DCTDecode（JPEG）或 FlateDecode（像素），独立导出后可做图片隐写分析。
5. **脚本**：`/JavaScript`、`/OpenAction`，有时 flag 在 JS 里。

**Office Open XML（docx/pptx/xlsx）本身就是 ZIP**，里面是 XML。藏法：`word/media/` 下多一张图、`docProps/custom.xml` 里的自定义属性、批注/修订记录、字体颜色为白色、`vbaProject.bin` 宏。老的 `.doc/.xls/.ppt` 是 **OLE 复合文档**（CFB），用 `olevba`、`oletools` 分析。

## 三、操作步骤

1. **`file` 判类型 + `binwalk`** 看有没有追加 ZIP/图片。
2. **看元数据**：`exiftool -a -u -g1`，PDF 的 `Title/Author/Keywords`。
3. **PDF 结构体检**：`pdfid`（看 JS/ObjStm/EmbeddedFile 计数）、`pdfdetach -list`。
4. **文本提取**：`pdftotext -layout`，白色文字一样能抽出来。
5. **提取对象**：`pdf-parser --object N`、`qpdf --qdf`（解压成可读流）、`mutool extract`（提取所有内嵌图片/字库）。
6. **Office 解压**：`7z x doc.docx -o out/`，翻 `word/media`、`docProps`。
7. **旧版 OLE**：`olevba`、`oleid`、`oleobj`。

## 四、命令/脚本

### PDF 一手排查

```bash
file target.pdf; binwalk target.pdf
exiftool -a -u -g1 target.pdf | head -40
pdfid target.pdf                       # 统计 /JS /JavaScript /OpenAction /EmbeddedFile /ObjStm
pdf-parser --stats target.pdf
pdfdetach -list target.pdf              # 列出内嵌附件
pdfdetach -saveall target.pdf           # 全部保存
pdftotext -layout target.pdf - | head -50
qpdf --qdf --object-streams=disable target.pdf unpacked.pdf   # 解压成明文对象
mutool clean -d target.pdf clean.pdf    # 等价路线的另一种选择
mutool extract target.pdf               # 导出所有图像/字体 -> image-0001.png ...
pdfimages -list target.pdf              # 列出图像对象
pdfimages -all target.pdf img            # 导出为 png/jpg
```

### 找旧版本（增量更新）

```bash
grep -c '%%EOF' target.pdf                  # >1 说明有增量更新
pdfresurrect -w target.pdf                  # 提取历史版本 -> version_*.pdf
# 或手工：按 %%EOF 切分，每段单独当 PDF 打开
python - <<'PY'
d = open('target.pdf','rb').read()
parts, start = [], 0
while True:
    i = d.find(b'%%EOF', start)
    if i < 0: break
    parts.append(d[start:i+5]); start = i+5
for n, p in enumerate(parts):
    open(f'ver_{n}.pdf','wb').write(p)
print('versions:', len(parts))
PY
```

### 提取 PDF 里的图片后跑隐写

```bash
mutool extract target.pdf && ls
for f in image-*.png image-*.jpg; do
  [ -f "$f" ] && { echo "== $f"; zsteg -a "$f" 2>/dev/null | head -3; \
                   steghide info "$f" 2>/dev/null | head -3; }
done
```

### docx / pptx / xlsx

```bash
mkdir -p x && 7z x -y -o./x target.docx
find x -type f | sort
cat x/docProps/core.xml x/docProps/app.xml 2>/dev/null | head -5
ls -la x/word/media/ 2>/dev/null      # 所有内嵌图片
grep -o '<w:t[^<]*<' x/word/document.xml | head -40      # 文本
# 隐藏文字（vanish）、白色字体
grep -o '<w:vanish/>' x/word/document.xml | wc -l
grep -oE 'w:color w:val="[0-9A-Fa-f]{6}"' x/word/document.xml | sort | uniq -c
```

```python
#!/usr/bin/env python3
# docx_text.py —— 提取 docx 全部文本 + 图片清单 + 自定义属性
import zipfile, re, sys
z = zipfile.ZipFile(sys.argv[1])
for n in z.namelist():
    print('[-]', n)
xml = z.read('word/document.xml').decode('utf8', 'replace')
text = ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml, re.S))
print('[text]', text[:500])
for n in z.namelist():
    if n.startswith('word/media/'):
        open(n.split('/')[-1], 'wb').write(z.read(n))
        print('[img]', n, '->', n.split('/')[-1])
```

### 旧版 OLE（doc/xls/ppt）

```bash
pip install oletools
oleid target.doc
olevba target.doc | head -60
oleobj target.doc -o out/       # 导出内嵌对象
# 也可以直接把 .doc 当 zip 试（部分假 doc 实际是 docx）
unzip -l target.doc 2>/dev/null
```

## 五、常见坑 / 变体

- **PDF 打开空白页但 pdftotext 有字**：文字被移到页面外坐标（`x=-9999`），导出后即可见。
- **`mutool extract` 输出的图名形如 `image-0001.png`**，注意有的版本输出到 `./extracted/`。
- **加密 PDF**：`qpdf --password= -decrypt in.pdf out.pdf`（空密码）；`pdf2john` + `john` 跑字典。
- **docx 里藏 zip**：`word/media/` 里可能有 `image1.png` 实际是 ZIP，`file` 一下。
- **批注/修订**：`word/comments.xml`、`w:ins`/`w:del` 里的内容常是 flag 前半段 + 后半段。
- **PPTX 的备注**：`ppt/notesSlides/` 里藏着 speaker notes。
- **文件扩展名伪装**：老的 `flag.txt` 其实是 PDF，`file` 一定先跑。

## 六、参考来源

- [Aperi'Solve 速查表（Documents / PDF 分支）](https://www.aperisolve.com/cheatsheet)
- [pdfid & pdf-parser 官方文档（Didier Stevens）](https://blog.didierstevens.com/programs/pdf-tools/)
- [qpdf 手册（解密/线性化/解对象流）](https://qpdf.readthedocs.io/)
- [mutool 手册页（extract/clean）](https://www.mankier.com/1/mutool)
- [oletools 官方仓库](https://github.com/decalage2/oletools)
- [OOXML 打包结构（Microsoft Open Specifications）](https://learn.microsoft.com/openspecs/office_standards/ms-oi29500/)
