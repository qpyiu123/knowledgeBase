# CTF 知识库索引

共 **241** 条，覆盖 **11** 个方向。
本文件由 `python tools/gen_index.py` 自动生成，请勿手改。

> 用法：`kb search "题面关键词"` 模糊查；`kb ask "题目描述"` 让本地模型给思路。

## 方向总览

| 方向 | 条目数 | 说明 |
|---|---|---|
| [杂项 Misc](#misc) | 28 | |
| [密码学 Crypto](#crypto) | 25 | |
| [逆向 Reverse](#reverse) | 30 | |
| [二进制利用 Pwn](#pwn) | 36 | |
| [Web](#web) | 42 | |
| [取证 Forensics](#forensics) | 22 | |
| [移动端 Mobile](#mobile) | 14 | |
| [区块链 Blockchain](#blockchain) | 6 | |
| [硬件 Hardware](#hardware) | 14 | |
| [情报 OSINT](#osint) | 12 | |
| [AI 安全](#ai) | 12 | |

<a id="misc"></a>
## 杂项 Misc (28)

- 🟢 [shell 与脚本一行流（awk/sed/grep/perl 提取比赛数据）](misc/shell-oneliner-tricks.md) — _题目给了一个巨大的日志或者 csv 让你统计某个字段、需要从几千行输出里提取符合格式的字符串、题目要求把十六进制 dump 还原成文件、给的是一个超大的文本里藏着按规律排列的 flag 字符_
- 🟢 [二维码与条码识别（残缺二维码 / Aztec / DataMatrix）](misc/qr-and-barcode.md) — _附件是一张二维码、二维码缺了三个角、二维码被打了马赛克、扫码结果只有一半 flag_
- 🟢 [工具矩阵与 WSL 常用命令（CyberChef/StegSolve/hex 工具箱）](misc/cyberchef-and-tools.md) — _Windows 上没有 Linux 工具、不想装虚拟机、需要一次性环境、binwalk 报错_
- 🟢 [文件头识别与常见魔数速查](misc/file-signature-identify.md) — _附件没有后缀名、改了后缀打不开、文件提示 corrupted、打开是乱码_
- 🟢 [文档隐写（PDF 对象流 / docx、pptx 解压 / OLE）](misc/pdf-and-doc.md) — _附件是 pdf 或 docx、文档打开后只有几行字、文件体积偏大、pdf 里有多个 EOF_
- 🟢 [杂项通用检查清单（file → strings → binwalk → 分离 → 分析）](misc/misc-checklist.md) — _附件不知道从哪下手、题目类型没写、试了几个工具都没出、时间不够想按套路走_
- 🟢 [流量包入门（pcap 快速定位与数据提取）](misc/misc-network-hands.md) — _附件是 pcap/pcapng、题目说你截到了流量、流量文件很大、需要找上传的文件_
- 🟢 [编码套娃（base64/base32/base85/URL/Hex/XXencode）](misc/encoding-chain.md) — _给了一长串字符、结尾有等号、字符串只有大小写字母和数字、满屏百分号_
- 🟡 [BMP/GIF/TIFF 隐写进阶（调色板/帧延迟/扩展标签）](misc/bmp-gif-tiff-stego.md) — _给了一个 .bmp 或 .gif 或 .tif、图片颜色明显变灰变脏有噪点、调色板里出现大量重复或近似色、GIF 每帧延迟大量为 0_
- 🟡 [JPG 图片隐写（DCT/outguess/steghide/EXIF）](misc/jpg-steganography.md) — _给了一张 jpg、zsteg 在 jpg 上没结果、图片里有密码提示、文件尾部有额外数据_
- 🟡 [LSB 与频谱图分析（StegSolve / Aperi'Solve / Audacity）](misc/lsb-analysis.md) — _图片位平面像随机噪声、隐写工具都解不出、题目提示颜色或通道、音频听起来是杂音_
- 🟡 [PNG 图片隐写排查（binwalk/zsteg/CRC 宽高/LSB/IDAT）](misc/png-steganography.md) — _给了一个 png、打开图片被裁切、图片下半部分全黑、文件大小远大于像素数据_
- 🟡 [Python 沙箱逃逸（pyjail / misc 向）](misc/pyjail-escape.md) — _题目是 python 即兴输入、屏蔽了 os 和 builtins、有黑名单过滤括号或引号、需要 cat flag.txt_
- 🟡 [ZIP 压缩包技巧（伪加密/明文攻击/CRC 爆破）](misc/zip-archive-tricks.md) — _给了一个加密压缩包、解压要密码但题面没给、同一个 readme 出现两份、压缩包里有 4 字节小文件_
- 🟡 [内存 / 进程 dump 分析（misc 向：strings、堆块、回写文件）](misc/memory-dump-misc.md) — _附件是一个几十 MB 到几个 GB 的 vmem 或 raw 或 dmp、题目说这是某个进程崩溃时的内存转储、文件里能 strings 出 flag 但被切成几段、题目给了个 pid 或者进程名_
- 🟡 [冷门编码家族（UTF-7/16、EBCDIC、rot47、base91/92、QP、Punycode）](misc/rare-encoding-family.md) — _密文里出现大量反斜杠加号开头的片段、hex 里每隔一个字节是 00 或者 0x00 后置、字符集里有 + - * / 和大量标点但读不出单词、编码结果里有大量的等号后面跟两个十六进制_
- 🟡 [压缩包进阶（7z/RAR 口令破解、嵌套、头部损坏修复）](misc/archive-cracking-advanced.md) — _题目给了 7z 或 rar 并且打开就要密码、压缩包里套压缩包一共套了五层以上、密码提示是四位数字或者生日格式、rar 版本提示是 RAR5_
- 🟡 [图片取证（ELA、拼接检测、重压缩与深度伪造识别）](misc/image-forensics-tampering.md) — _题目要求判断图片是否被篡改或者哪一块被 P 过、图片里有一块区域的噪点明显比周围干净、题目给了原始图和处理后图要求找差异区域、图片里某个人脸边缘有模糊或者重影_
- 🟡 [文件修复与损坏识别（手工重建头部、CRC 重算）](misc/file-repair-and-corruption.md) — _文件打不开提示已损坏、file 命令识别不出类型或者识别成 data、十六进制里文件头魔数被改了一两个字节、pngcheck 报 CRC error 或 truncated_
- 🟡 [杂项冷门题型（时间戳/元数据/隐写音频/文件时间线）](misc/ctf-osint-collection.md) — _题目只给了一张图和几个数字、附件是一堆文件没有内容、文件名里有奇怪的时间、元数据里有可疑字段_
- 🟡 [视频隐写（MP4/MKV box 结构、帧级隐写、ffmpeg 提取）](misc/video-steganography.md) — _给了一段 mp4 或 mkv 视频、视频结尾黑屏但时长还有几秒、某些帧画面闪一下就能看到一行字、视频里只有一帧和别的不一样_
- 🟡 [语言级沙箱逃逸（Lua / bashjail / Ruby / JS 沙箱）](misc/sandbox-escape-lua.md) — _题目是 lua 交互环境、给了个功能受限的 shell、允许输入但禁止 cat、只能用一部分命令_
- 🟡 [非 HTTP 协议交互 misc（nc 脚本、Telnet/SSH/SMTP 手工对话）](misc/nc-protocol-interaction.md) — _题目给了 nc 地址和端口而不是 http 链接、连上去是一个菜单式的文字界面要求选 1-5、协议返回 220 开头或者 SSH-2.0- 开头的横幅、服务端要求输入密码但没有任何提示词_
- 🟡 [音频隐写（频谱/DTMF/莫尔斯/LSB/SSTV）](misc/audio-steganography.md) — _附件是 wav 或 mp3、音频里有嘀嘀声、音频听起来像杂音、播放时有规律的嘟嘟声_
- 🔴 [垃圾代码与程序流反转（junk code / gml 脚本）](misc/gml-junk-code.md) — _程序里有一堆无关指令、反汇编出现 call 后紧跟垃圾字节、程序逻辑看起来是反的、输入正确却说错误_
- 🔴 [数学与算法类 misc（大数分解、矩阵、迷宫、自动机）](misc/math-and-algorithm-misc.md) — _题目给了一张地形图要求从左上走到右下、给了一个巨大的整数要求分解或者求因子、给出了矩阵乘法结果要求反推原矩阵、输入里有长度上千的01序列和状态转移表_
- 🔴 [游戏 / 交互型 misc（概率逆推、模拟器输入、AI 对手）](misc/game-and-interactive-misc.md) — _附件是一个自制小游戏需要打到某个分数才能给 flag、服务器端 nc 连上去是一个猜数字或者 21 点游戏、游戏随机数用的是 std::rand 或 mt19937、题目说要连胜 20 局才能拿 flag_
- 🔴 [编码自动识别（写一个多层编码侦探脚本）](misc/encoding-auto-detect.md) — _题目给了一段看不出是什么编码的字符串、密文解一层后还是乱码需要继续解、字符串里混了 base64 和 rot13 和 hex 三层、题目一串字段给出来看着像密文但没有明确提示_

<a id="crypto"></a>
## 密码学 Crypto (25)

- 🟢 [AES-ECB 分组相等分析（ECB Penguin）](crypto/aes-ecb-penguin.md) — _ecb 模式、相同明文块产生相同密文块、可以控制输入前缀、加密后返回密文_
- 🟢 [RSA Fermat 分解（p、q 相近）](crypto/rsa-fermat-factorization.md) — _p 和 q 很接近、p q 差值很小、两个素数相邻、nextprime_
- 🟢 [RSA dp 泄露攻击](crypto/rsa-dp-leak.md) — _给了 dp、题目吐出 dp、dq 或 dp、e d p q 部分已知_
- 🟢 [RSA 小公钥指数攻击（小明文开方 / Coppersmith）](crypto/rsa-small-e-attack.md) — _e=3、e 很小、公钥指数只有 3、密文长度和 n 差不多但 e 是 3_
- 🟢 [古典密码（Atbash / 凯撒 / 维吉尼亚 / 仿射 / 巴利克）](crypto/classical-cipher.md) — _全字母无数字、密文看起来像乱码但只是字母、凯撒移位、维吉尼亚_
- 🟢 [弱 RSA 共模攻击](crypto/rsa-common-modulus-attack.md) — _两组密文、e 不同、n 相同、gcd(e1_
- 🟡 [AES-CBC 字节翻转 / 逐字节解密（Padding Oracle）](crypto/aes-cbc-byte-at-a-time.md) — _cbc 模式、密文十六进制很长、iv 可篡改、已知明文前缀_
- 🟡 [CRT 同余方程组与 DH 小型子群攻击（Pohlig-Hellman）](crypto/crt-dh-small-subgroup.md) — _给了多组不同的模数、同一明文 mod 多个 n、模数满足 a ≡ b mod 小素数、给出了 p-1 的因子分解_
- 🟡 [DES/3DES 弱密钥与 2DES 中间相遇（MITM）](crypto/des-3des-weakkey-mitm.md) — _加密用了 DES、加密用了 3DES、代码里 DES.new 调了两次、密钥是 8 字节重复_
- 🟡 [ECC 小阶 / 无效曲线攻击（Invalid Curve / Small Subgroup）](crypto/ecc-small-order.md) — _椭圆曲线、ecc、只给了点坐标没有 a b、点可以自由提交_
- 🟡 [ElGamal / Paillier / Rabin 同态性质与攻击面](crypto/elgamal-paillier-rabin-homomorphic.md) — _加密结果可以相乘后解密、题目给了 (c1 c2) 两元组、提到了加法同态、paillier 的 g 等于 n+1_
- 🟡 [LFSR 关联攻击 / BM 算法（线性反馈移位寄存器）](crypto/lfsr-attack.md) — _线性反馈移位寄存器、lfsr、输出比特流、钥流_
- 🟡 [MT19937 随机数破译（untemper）](crypto/random-mt19937.md) — _random.getrandbits、python 的 random、624 个输出、随机数预测_
- 🟡 [OTP / Many-Time-Pad 与 CRIB 拖拽还原](crypto/otp-many-time-pad.md) — _多段密文长度接近且看起来等长、xor 后出现大量可见字符、题目说密钥流重复使用、一次性密码本却被复用_
- 🟡 [RSA CRT 故障注入（Bellcore）与签名故障恢复 n](crypto/rsa-crt-fault-injection.md) — _服务端用 CRT 做签名、同一消息签了两次结果不同、给了两组合法签名和错误签名、计算 d mod p 时不加随机延迟_
- 🟡 [RSA 低加密指数广播攻击（Håstad）](crypto/rsa-broadcast-attack.md) — _多组密文、多个 n、e 相同且很小、e=3_
- 🟡 [RSA 维纳攻击（d 过小 / e 过大）](crypto/rsa-wiener-attack.md) — _e 非常大、e 和 n 位数差不多、e 比 n 还大、d 很小_
- 🟡 [Shamir 秘密共享与多项式插值还原](crypto/shamir-secret-sharing.md) — _题目给定 threshold 门限 t、给了 t 个子秘密分享点、分享点是 (x y) 坐标对、源码里出现 random 多项式系数_
- 🟡 [哈希长度扩展攻击（Hash Length Extension）](crypto/hash-length-extension.md) — _md5(secret+data)、sha1(key+msg)、MAC 可被伪造、已知 hash 值和消息_
- 🟡 [线性同余随机数预测（LCG）](crypto/lcg-predict.md) — _线性同余、rand() 输出、连续随机数、a b m 参数_
- 🟡 [跨语言随机数预测（Java Random / PHP mt_rand / Python random）](crypto/cross-language-prng-predict.md) — _题目用 java.util.Random、源码里出现 nextInt 或 nextLong、密钥来自 Random 种子、种子是时间戳或 System.currentTimeMillis_
- 🔴 [ECDSA/EdDSA 随机数重用与偏置 nonce（格攻击）](crypto/ecdsa-nonce-reuse-lattice.md) — _两次签名 r 相同、签名是 (r s) 二元组、源码里 k = 固定值或 from_bytes、nonce 只用了 8 位_
- 🔴 [RSA Padding Oracle 攻击（Bleichenbacher / PKCS#1 v1.5）](crypto/rsa-padding-oracle.md) — _padding error、解密成功或失败的返回不同、服务器会告诉你填充对不对、PKCS#1 v1.5_
- 🔴 [RSA 已知高位攻击 / Coppersmith 小根](crypto/rsa-coppersmith.md) — _已知 p 的高位、给了 p 的部分比特、已知 m 的高位、明文前几位已知_
- 🔴 [格攻击入门（LLL / Coppersmith 载体构造）](crypto/lattice-lll.md) — _格、lattice、lll 算法、背包_

<a id="reverse"></a>
## 逆向 Reverse (30)

- 🟢 [.NET / C# 逆向（dnSpyEx / ILSpy）与 Unity il2cpp](reverse/dotnet-unity-il2cpp.md) — _文件是 .NET 程序集、有 mscoree.dll 导入或 CLR 头、Unity 游戏里有 GameAssembly.dll 与 global-metadata.dat、反编译能看到完整 C# 源码_
- 🟢 [Python 字节码逆向（pyc / pycdc / decompyle3 差异）](reverse/pyc-reverse.md) — _附件是 .pyc 或 __pycache__、文件头是 0x55 0x0d 0x0d 0x0a、只有 pyc 没有源码、反编译工具报 Unknown opcode_
- 🟢 [UPX 脱壳与手动脱壳（Windows / Linux）](reverse/packed-upx.md) — _strings 里几乎什么都没有、段名是 UPX0/UPX1、自解压循环、入口处有 pushad/popad_
- 🟢 [x86 / x64 汇编速查（与做题强关联）](reverse/assembly-basics.md) — _看反汇编看不懂寄存器在干嘛、需要手写 shellcode、需要 patchelf 改指令、不熟 64 位调用约定_
- 🟢 [补丁与 crackme 型题目（patch 思路与 keygen 生成）](reverse/patch-and-keygen.md) — _程序要求输入序列号或注册码、输入错误弹窗 "Invalid license"、验证函数里只有一个条件跳转决定成败、题面要求「给出注册机」或「patch 后能跑」_
- 🟢 [逆向工具链与快捷键速查（IDA / Ghidra / Binary Ninja / radare2）](reverse/rev-toolchain.md) — _拿到 exe/elf 不知用哪个工具、需要批量看函数、想用命令行自动化、团队里工具不统一_
- 🟡 [Android APK 逆向与 native so 分析](reverse/android-basics.md) — _附件是 .apk、有 lib/arm64-v8a/*.so、Java 层逻辑很少、校验在 native 层_
- 🟡 [Electron / JS 混淆还原](reverse/electron-reverse.md) — _附件是 .asar 或 resources/app 目录、有 app.asar / electron.asar、js 里满是 _0x1a2b 变量名、有 if/else 嵌套控制流_
- 🟡 [Frida 动态分析二进制（native hook、trace、内存 dump）](reverse/frida-dynamic-analysis.md) — _需要在不改文件的情况下观察函数参数与返回值、程序有强完整性校验无法直接 patch、目标是 APK / iOS / 桌面原生程序、需要 dump 解密后的内存数据_
- 🟡 [Ghidra 反编译实战流程](reverse/static-analysis-ghidra.md) — _只有 Ghidra 可用（无 IDA 授权）、需要批量分析上千函数、需要写脚本自动找 flag 校验、需要还原结构体与函数签名_
- 🟡 [Golang 逆向（恢复函数名与结构体）](reverse/golang-reverse.md) — _二进制很大且静态链接、出现 runtime.morestack_noctxt、反编译里满是 goroutine 相关代码、函数名是 sub_xxx 但字符串有大量 Go 路径_
- 🟡 [IDA 插件与 Python 自动化（批量分析、自动改名、反编译导出）](reverse/ida-python-automation.md) — _目标函数上千个且需要批量处理、需要把伪代码批量导出成文本、有大量逐字节比较函数需要自动识别、题面要求「找出所有引用 X 的地方」_
- 🟡 [Lua / Python 脚本保护与字节码还原（Luac 反编译、混淆 Lua）](reverse/lua-bytecode-decompile.md) — _附件以 1b4c7561 开头（Lua 字节码魔数）、文件出现 Lua 5.1 或 Lua 5.3 字样、脚本被封装进 exe 且字符串里有 lua_pcall、混淆后的变量名形如 O0O0O / lIll_
- 🟡 [Rust 逆向要点（符号还原 / 结构体 / 内存安全）](reverse/rust-reverse.md) — _字符串里出现 core::panicking、有 rust_begin_unwind、函数名形如 _ZN...17h...E、二进制里有大量 Result/Option 处理_
- 🟡 [WebAssembly 逆向（wasm 反编译与还原）](reverse/wasm-reverse.md) — _附件是 .wasm 或 .wat、文件开头是 \0asm、网页里 fetch 加载 wasm、题目用 emscripten 编译_
- 🟡 [angr 符号执行求 flag](reverse/angr-symbolic-execution.md) — _校验逻辑复杂且分支极多、输入逐字节比较、有大量 if/else 且无法反推、需要自动化跑出正确输入_
- 🟡 [z3 约束求解还原算法](reverse/z3-solve.md) — _校验是纯算术没有复杂分支、输入长度固定 10~64、有大量异或与移位、需要逆推输入_
- 🟡 [反调试与绕过（IsDebuggerPresent / ptrace / TracerPid）](reverse/anti-debugging.md) — _下断点程序直接退出、程序跑起来检测到调试器就崩、单步走两步就跳飞、进程名带 debug 就报错_
- 🟡 [算法还原套路（TEA / XXTEA / RC4 / 自定义变换的识别特征）](reverse/crypto-algorithm-identify.md) — _反编译里出现 (v5 << 4) ^ (v5 >> 5) 这种移位+异或组合、常量 0x9E3779B9 或 0x61C88647 出现在代码里、有一个 256 字节的 S 盒初始化循环，随后两次 swap、输入按 8 字节一组处理，长度必须是 8 的倍数_
- 🔴 [Flutter / Dart AOT 逆向（libapp.so 与 Blutter）](reverse/flutter-dart-aot.md) — _APK 的 lib 目录下有 libapp.so 且体积超过 5MB、没有 libflutter_engine.so 只有 libflutter.so、程序 UI 有 Flutter 的 Material 控件风格、反编译 dex 只看到 MainActivity 与 FlutterActivity_
- 🔴 [Go 二进制闭包与 goroutine 还原（runtime 结构逆向）](reverse/go-closure-goroutine.md) — _二进制里有 runtime.main 或 runtime.goexit 符号、字符串里有 build id 与 Go build ID、反编译出大量形如 pclntab 的表、有 runtime.newproc 或 goexit 调用_
- 🔴 [LuaJIT 字节码与手游脚本逆向（lj_bc 还原）](reverse/luajit-bytecode.md) — _文件头是 1b4c4a（1b 4c 4a）、出现 LuaJIT 2.0 或 LuaJIT 2.1 字样、手游包里有 libcocos2dlua.so 或 libluajit.so、assets 目录下大量 .lua 但是二进制_
- 🔴 [Solidity / EVM 字节码反编译（合约反汇编与 storage 还原）](reverse/evm-solidity-bytecode.md) — _附件是 .sol 源码或 0x60 开头的十六进制字节码、题目给了一个合约地址与 RPC 节点、有 Bytecode 字段且以 6080604052 开头、提示「合约」「链」「以太坊」「部署」_
- 🔴 [Unity il2cpp 进阶（global-metadata.dat 还原与 Il2CppDumper 全流程）](reverse/unity-il2cpp-advanced.md) — _APK 里有 libil2cpp.so 且伴随 global-metadata.dat、PC 游戏有 GameAssembly.dll 与 global-metadata.dat、用 dnSpy 打开只看到 Assembly-CSharp 的空壳、报错 "Unable to resolve" 或 "metadata version mismatch"_
- 🔴 [Windows 内核驱动逆向（DriverEntry、IRP、IOCTL 分析）](reverse/windows-kernel-driver.md) — _文件是 .sys 后缀且 PE 特征为 driver、存在 DriverEntry 导出或入口、字符串里有 \\Device\\ 与 \\DosDevices\\ 前缀、导入表只有 ntoskrnl.exe 与 HAL_
- 🔴 [反编译失败时的动态调优（混淆对抗与断点定位关键比较）](reverse/decompile-failure-dynamic-tuning.md) — _IDA 反编译报 "call analysis failed" 或大量 jmp 到未知块、函数被拆成上千个基本块且无逻辑、存在 IsDebuggerPresent 或 ptrace 检测、程序在调试器下直接崩溃或退出_
- 🔴 [固件 / IoT 逆向（固件镜像解包与嵌入式二进制分析）](reverse/firmware-iot-reverse.md) — _附件是 .bin / .img / .hex 固件包且体积 4MB~64MB、binwalk 能看出 SquashFS 或 CramFS 文件系统、镜像里有 UBI / UBI# 标记、字符串里有 BusyBox 与 OpenWrt 字样_
- 🔴 [符号执行进阶（angr CFG / reaching、Triton、Manticore 对比）](reverse/symbolic-execution-advanced.md) — _程序校验逻辑有大量位运算与分支、输入长度固定且只有 16~64 字节、校验失败输出 "wrong" 且无任何提示、静态反编译出上千行的位级运算_
- 🔴 [花指令与控制流平坦化还原（含 IDA 脚本）](reverse/obfuscation-junk.md) — _IDA 反编译报 call analysis failed、函数里出现 jmp 跳到中间、有大量无意义 xor/nop、一个主循环 + 状态变量分发_
- 🔴 [虚拟机保护与自研 VM handler 还原](reverse/vm-protection.md) — _主循环里有巨大的 switch 或跳转表、大量重复的小函数、程序里出现 bytecode 数组、控制流是「取指令-解码-执行」_

<a id="pwn"></a>
## 二进制利用 Pwn (36)

- 🟢 [Pwn 环境搭建（pwntools / pwndbg / patchelf / glibc-all-in-one）](pwn/pwn-tools-setup.md) — _新机器要配 pwn 环境、本地能过远程不过、ldd 显示系统 libc 与题目不一致、需要多版本 libc 切换_
- 🟢 [checksec 与保护机制判读速查](pwn/checksec-and-basics.md) — _拿到二进制先 checksec、题目给了 libc.so.6、远程 nc 可交互、Dockerfile 里写了 ubuntu:20.04_
- 🟢 [pwn 自动化工具链 —— pwntools 模式、one_gadget、QEMU 与 gdb-multiarch](pwn/pwn-automation-toolchain.md) — _题目给了 libc 但本地环境 glibc 版本不一致需要 patchelf、需要跨架构调试 arm 或 aarch64 二进制、想批量爆破 one_gadget 约束条件、手写 exp 交互太繁琐要写模板_
- 🟢 [基础栈溢出 ret2text / ret2shellcode](pwn/stack-overflow-ret2text.md) — _gets/read 读入 buf 且长度超限、程序里有 win 函数、PIE 关闭、NX 关闭_
- 🟡 [ARM / AArch64 pwn 入门 —— 交叉编译、ARM 汇编要点与 ROP 构造](pwn/arm-aarch64-pwn.md) — _file 显示 ARM aarch64 或 arm 32 位小端、题目只给一个 elf 没有给运行环境、需要 qemu-arm 或 qemu-aarch64 才能运行、没有 system 但有很多 pop 和 bx 指令_
- 🟡 [ASLR 爆破技巧（canary / PIE / libc 低位）](pwn/aslr-bruteforce.md) — _服务每次连接都崩溃但不重启、nc 连上后进程 fork 出来、只能部分覆盖地址、低12位固定_
- 🟡 [Canary 绕过四种打法（泄露 / 爆破 / __stack_chk_fail / TLS）](pwn/stack-canary-bypass.md) — _checksec 显示 Canary found、程序里出现 __stack_chk_fail、fork 服务且每次连接重启、有 puts/printf 输出缓冲区_
- 🟡 [PIE 绕过 —— 部分覆盖与信息泄露](pwn/pie-bypass.md) — _checksec 显示 PIE enabled、无输出函数无法泄露、溢出只需改返回地址低2字节、程序有 read 无 write/puts_
- 🟡 [UAF 与堆溢出综述（题型 / 原语 / 利用路线图）](pwn/heap-uaf-heapoverflow.md) — _菜单式 add/del/edit/show、free 后指针未清、edit 长度不校验、存在 off-by-one 或 off-by-null_
- 🟡 [Windows pwn 入门 —— ASLR/DEP/CFG 保护、栈溢出与 SEH 利用](pwn/windows-pwn-basics.md) — _附件是 exe 或 dll 而不是 elf、题目要求 nc 到一个 windows 服务端口、程序使用 recv 或 fgets 读入并 strcpy 到栈缓冲区、崩溃时异常处理器地址被覆盖_
- 🟡 [__malloc_hook / __free_hook 与 2.34+ 替代方案](pwn/malloc-hook-tricks.md) — _题目 libc 2.23~2.33、有任意写能力、需要一次 malloc 或 free 就拿到 shell、2.34 后 __free_hook 找不到_
- 🟡 [glibc 2.27 ~ 2.41 版本差异速查（Pwn 视角）](pwn/glibc-version-diff.md) — _拿到新 libc 不知道能用哪招、writeup 跑不通、__free_hook 找不到、unaligned tcache chunk detected_
- 🟡 [partial overwrite 与受限单字节 / OOB 写](pwn/partial-overwrite-oob.md) — _输入长度只比缓冲区多 1 字节、只能改写地址的最低 1 到 2 个字节、程序没有任何输出函数无法泄漏地址、PIE 开启但目标与返回地址同页_
- 🟡 [ret2csu 与 gadget 搜索（ROPgadget / ropper）](pwn/ret2csu.md) — _二进制里找不到 pop rsi、只有 pop rdi 一个参数 gadget、64 位小体积二进制、静态链接但 gadget 稀少_
- 🟡 [ret2libc —— libc 基址泄露与 system("/bin/sh")](pwn/ret2libc-offset-leak.md) — _题目附带 libc.so.6、只有 puts/write 无 system、NX 开启且无 win 函数、有 canary 但无 PIE_
- 🟡 [ret2syscall 与 SROP 全寄存器控制](pwn/ret2syscall.md) — _静态链接无 libc 符号、只有 syscall 无 system、栈溢出空间很小、read 长度只有 0x10_
- 🟡 [seccomp 沙箱下的 ORW（open/read/write）与沙箱绕过](pwn/sandbox-orw-seccomp.md) — _题目附件里有 seccomp 规则或 seccomp-tools 可用、拿到 shell 后 cat 没权限、execve 被拒绝返回-EPERM、题目提示 only read/write/open_
- 🟡 [unsorted bin 泄露 libc（2.23 ~ 2.35 通用）](pwn/heap-unsortedbin-leak.md) — _chunk 大小大于 0x408 会跳过 tcache、UAF show 能读出乱码地址、只能泄露不能写、题目 libc 给了但 heap 地址未知_
- 🟡 [栈迁移（leave; ret）与栈劫持](pwn/stack-pivot.md) — _溢出长度只够覆盖 rbp + 返回地址、栈空间不够放完整 ROP、二进制里有 leave ret gadget、存在可写 .bss 或堆地址泄露_
- 🟡 [格式化字符串任意读写（含 %n 覆盖 GOT）](pwn/format-string-arbitrary-write.md) — _printf(用户输入) 没有格式串、出现 %p %s %n 被过滤、程序先打印再读、栈上有 0x70257025 之类回显_
- 🔴 [1-day CVE 的 Pwn 化利用（PwnKit 与 Dirty Pipe）](pwn/one-day-cve-pwn.md) — _题目给了带版本的二进制和源码、附件提示内核版本 5.8~5.16、程序用到 argv/envp 边界、目标有 SUID 程序_
- 🔴 [FSOP 与 _IO_FILE 伪造 vtable（House of Orange / 2.34+）](pwn/heap-fsop-io-file.md) — _题目只有 malloc 没有 free、需要劫持 stdout 或 exit handler、__free_hook 已不可用、Full RELRO 无 GOT 可改_
- 🔴 [Fastbin attack —— fastbin dup / into stack / house of spirit](pwn/heap-fastbin-attack.md) — _小块 malloc 后连续 free、double free 未被检测、无 tcache 的 glibc 2.23 环境、有 __malloc_hook 可写_
- 🔴 [House of Einherjar —— 单 null 字节覆盖 size 造成堆重叠](pwn/heap-house-of-einherjar.md) — _只能往堆上多写一个 00 字节、下一个 chunk 的 prev_size 字段相邻且可控、程序能显示 chunk 地址或 heap 基址、chunk 的 size 低字节是 0x21 或 0x31 这类小值_
- 🔴 [House of Spirit 与 fastbin dup —— 区别、选择与分工](pwn/heap-house-of-spirit-vs-fastbin-dup.md) — _程序只有 malloc 没有 free、能写到栈变量或全局变量里、能在栈上布置一个伪 chunk 头、有一个 free 指针数组可以篡改_
- 🔴 [Linux 内核 pwn 入门（modprobe_path / commit_creds）](pwn/kernel-pwn-basics.md) — _附件有 bzImage 和 rootfs.cpio、启动脚本 run.sh 里有 -append、题目提供 .ko 模块、有 /dev/xxx 设备文件_
- 🔴 [glibc 2.34+ 的 IO 结构进阶 —— _IO_wfile / House of Kiwi / House of Cat](pwn/glibc-io-wfile-kiwi-cat.md) — _程序中有 stdin stdout stderr 的读写操作、能控制堆上内容但找不到 free_hook、glibc 版本 2.35 及以上、程序最后调用 exit 或主函数返回_
- 🔴 [large bin attack 与 House of Force / House of Lore](pwn/heap-largebin-house-of-force.md) — _glibc 2.31 及以上 unsorted attack 失效、需要写 largebin 指针到任意地址、能改 top chunk size、程序没有 free 只有 malloc_
- 🔴 [musl libc pwn —— mallocng 的 meta/group 结构差异与利用](pwn/musl-libc-pwn.md) — _二进制静态链接且 ldd 显示 not a dynamic executable、程序用 alpine 或 musl 编译、堆上找不到 tcache 或 main_arena、free 后 chunk 头部没有任何 size 字段_
- 🔴 [ret2dlresolve —— 无 libc 泄露时伪造动态链接解析结构拿 system](pwn/ret2dlresolve.md) — _程序里既没有 system 也没有 syscall、checksec 显示 Partial RELRO 或 No RELRO、没有格式化字符串也没有 UAF 泄露点、只导入 read 和 write 两个函数_
- 🔴 [seccomp 高级绕过 —— x32 ABI 混淆、openat2 与 TIOCSTI](pwn/seccomp-bypass-advanced.md) — _checksec 显示 seccomp 沙箱已启用且有 BPF 规则、只允许 open read write 而不允许 execve、规则里只检查 syscall 号没有检查 arch 字段、程序需要读取 flag 但 open 被禁用_
- 🔴 [tcache poisoning 与 safe-linking 绕过（2.26 ~ 2.41）](pwn/heap-tcache-dup.md) — _菜单式 add/del/edit/show 堆题、题目 libc 2.31 或 2.35、free 之后还能 edit (UAF)、double free 未检测_
- 🔴 [tcache stashing unlink attack —— small bin 遍历 + tcache 链构造](pwn/tcache-stashing-unlink.md) — _small bin 里有两个以上同尺寸 chunk、tcache 对应 bin 没有满但可以控制空闲个数、能通过 UAF 修改 small bin chunk 的 bk 指针、glibc 2.29 到 2.31 的题目_
- 🔴 [unsorted bin → large bin attack 利用链](pwn/largebin-attack-chain.md) — _需要往任意地址写一个堆地址、unsorted bin 里有两个不同尺寸的大 chunk、程序能 free 超过 0x410 的 chunk、已泄露堆地址但没有任意写原语_
- 🔴 [内核 pwn 进阶 —— kernel UAF、kmalloc-* 堆喷与 ret2dir](pwn/kernel-pwn-advanced.md) — _题目给 run.sh 启动 qemu 和 kernel 镜像、交互动的是 /dev 下的自定义字符设备、ioctl 里有 copy_from_user 和 kmalloc、目标是在内核态拿到 root 或读 flag_
- 🔴 [格式化字符串进阶 —— %hhn 分字节写、大数值写与多目标改写链](pwn/format-string-advanced-hhn.md) — _printf 的用户输入直接当作 format 参数、能控制格式化字符串但写入长度有限、程序只允许调用一次 printf、需要写多个地址比如 hook 加 fini_array_

<a id="web"></a>
## Web (42)

- 🟢 [SQL 注入基础（联合查询 / 盲注 / 时间盲注 + sqlmap）](web/sql-injection-basics.md) — _id=1 页面回显不同、单引号报错、you have an error in your sql syntax、可以排序 order by_
- 🟢 [命令注入与绕过](web/command-injection.md) — _ping 功能、执行系统命令、host 参数、system() 调用_
- 🟡 [CRLF 注入与 HTTP 响应拆分（Header 注入、Set-Cookie 劫持）](web/crlf-injection-response-splitting.md) — _跳转参数形如 ?url=/success，且 Location 头跟着用户输入变、用户名或上传文件名被回显进响应头、响应里出现 Set-Cookie，且其值来自用户输入、提交 %0d%0a 之后响应多出一个自定义头_
- 🟡 [CVE-2024-4577 PHP-CGI Windows 参数注入 RCE](web/cve-2024-4577-php-cgi-rce.md) — _windows 上的 php、xampp、php-cgi.exe、中文或日文 locale_
- 🟡 [Fastjson 反序列化（autoType / @type）](web/fastjson-autotype.md) — _fastjson 依赖、json 请求体、有 type 字段注入、autoType_
- 🟡 [GraphQL 攻击（introspection、别名批量绕过限流、字段建议泄露、注入）](web/graphql-attack.md) — _完整路径只有 /graphql，且所有请求都是 POST JSON、报错内容为 Cannot query field 并附带 Did you mean、响应 JSON 里有 errors[0].message 与 locations 字段、前端 JS bundle 里出现 __schema 或 gql 模板串_
- 🟡 [JS 原型链污染（Prototype Pollution）](web/nodejs-prototype-pollution.md) — _nodejs 应用、lodash 依赖、merge 对象、用户可控 json 键名_
- 🟡 [JWT 伪造（none 算法 / 密钥爆破 / RS256→HS256）](web/jwt-forge.md) — _jwt token、eyJhbGciOi、cookie 里是 jwt、authorization bearer_
- 🟡 [Jolokia / iBatis 等常见 Java 组件利用](web/jolokia-realm.md) — _jolokia 路径、/actuator、jmx 端点、5077 端口_
- 🟡 [Log4Shell CVE-2021-44228（JNDI 注入）](web/jndi-log4shell.md) — _日志里出现 jndi 关键字、用户输入被日志记录、log4j 2.x 依赖、java 应用_
- 🟡 [NoSQL 注入（MongoDB 操作符注入）](web/nosql-injection.md) — _登录框 返回 json、mongodb、参数是 json、$ne_
- 🟡 [PHAR 反序列化（phar:// 触发）](web/phar-deserialization.md) — _phar://、file_exists、is_file、file_get_contents_
- 🟡 [PHP 反序列化之原生类利用（SoapClient / SimpleXMLElement / Error）](web/php-native-class-gadget.md) — _unserialize 的参数完全可控，但全站没有自定义类、源码只有 flag.php 和 index.php，highlight_file 之后直接反序列化、报错页出现 SoapClient::__doRequest 或 Could not connect to host、题面提示词出现 原生类 / 没有 pop 链 / natives / SoapClient_
- 🟡 [PHP 反序列化（__wakeup / __destruct / POP 链）](web/php-deserialization.md) — _unserialize 用户输入、cookie 里是序列化数据、魔术方法、__destruct_
- 🟡 [Python pickle 反序列化 & pyjail 逃逸](web/python-pickle-pyjail.md) — _pickle.loads、反序列化、python 沙箱、禁用了 builtins_
- 🟡 [SQL 注入 WAF 绕过技巧集](web/sql-injection-waf-bypass.md) — _被 waf 拦截、403、请求被防火墙阻断、关键词被过滤_
- 🟡 [SSI / Servlet 冷门注入点（含 JSP/EL 注入）](web/ssi-servlet.md) — _shtml 文件、ssi 指令、Apache SSI、tomcat 报错页_
- 🟡 [SSRF 服务端请求伪造（内网穿透 / gopher 打 Redis / 云元数据）](web/ssrf-internal-access.md) — _url 参数、远程图片加载、webhook 回调、可以请求任意地址_
- 🟡 [SSTI 模板注入（Jinja2 / Twig / Freemarker）](web/ssti-template-injection.md) — _输入被渲染到页面模板、提交 7*7 回显 49、模板引擎报错、用户名欢迎语_
- 🟡 [Shiro-550 / Shiro-721（rememberMe 反序列化）](web/shiro-550-rememberme.md) — _rememberMe cookie、响应里有 deleteMe、cookie 值很长以 base64 结尾、Apache Shiro_
- 🟡 [XSS 跨站脚本（含 CSP 绕过）](web/xss-and-csp.md) — _输入被回显到 html、留言板、反射型 xss、搜索关键词回显_
- 🟡 [XXE 外部实体注入（含 Blind OOB / SSRF 组合）](web/xxe-injection.md) — _xml 上传、soap 接口、解析 xml 报错、doctype_
- 🟡 [文件上传绕过（含 .htaccess / 条件竞争）](web/file-upload-bypass.md) — _上传头像、upload.php、只允许 jpg png、检查 content-type_
- 🟡 [文件包含 LFI/RFI（php://filter / 日志包含）](web/lfi-rfi-and-log-poisoning.md) — _include 参数、file 参数、page 参数、path 参数_
- 🟡 [条件竞争（Race Condition）利用](web/race-condition.md) — _并发、兑换码、提现、投票_
- 🔴 [CSS 注入与 XS-Leak（选择器泄露、跨站状态泄漏）](web/css-injection-xs-leak.md) — _输入被放进 <style> 或 style 属性里、过滤了 <script> 但允许 <style> 和 @import、提示「无 JS」「CSP 禁止内联脚本」、页面会显示 flag 形式的字符串作为属性值_
- 🔴 [CVE-2024-21626 runc 容器逃逸（Leaky Vessels）](web/cve-2024-21626-runc-container-escape.md) — _docker 容器、runc、容器逃逸、文件描述符泄露_
- 🔴 [CVE-2024-3400 PAN-OS GlobalProtect 命令注入（10.0 分）](web/cve-2024-3400-panos-globalprotect.md) — _palo alto、globalprotect、pan-os、防火墙_
- 🔴 [CVE-2024-6385 GitLab 以任意用户身份运行 Pipeline](web/cve-2024-6385-gitlab-pipeline.md) — _gitlab 实例、可以导入群组、direct transfer、ci_job_token_
- 🔴 [Docker / K8s 场景下的 Web 逃逸（docker.sock 挂载、runc 漏洞）](web/docker-k8s-escape.md) — _拿到 webshell 后发现 /var/run/docker.sock 可读写、目录里有 /.dockerenv 文件、容器内 ls / 看到 docker 命令行工具、提示「容器」「逃逸」「宿主机」_
- 🔴 [HTTP 请求走私（CL.TE / TE.CL / TE.TE 与 H2 降级）](web/http-request-smuggling.md) — _响应头 Server: nginx，但报错栈是 Tomcat 或 Gunicorn、响应里出现 Via: 或 X-Cache: 说明存在反向代理层、构造非法 chunked 请求后，下一个请求才返回 400、题面提示词出现 反代 / 前后端不一致 / smuggling_
- 🔴 [JNDI 注入 + JDWP / RMI 利用](web/jndi-jdwp.md) — _jndi lookup、rmi 端口、5005 端口、jdwp 调试_
- 🔴 [Java 反序列化（CC 链 / ysoserial / JNDI）](web/java-deserialization.md) — _java 反序列化、commons-collections 依赖、readObject、base64 收到 rO0AB 开头_
- 🔴 [Java 模板注入进阶：Freemarker / Velocity / SpEL 执行链](web/ssti-java-freemarker-spel.md) — _输入被渲染后 ${7*7} 直接回显 49、报错栈出现 freemarker.template.TemplateException、报错栈出现 org.apache.velocity 或 VelocityEngine、参数被 @Value 或 SpelExpressionParser 求值_
- 🔴 [OAuth 2.0 / OIDC 与 SSO 绕过（redirect_uri、state、账号接管）](web/oauth-oidc-sso-bypass.md) — _登录页有「使用 GitHub 登录」「使用 Google 登录」按钮、URL 里出现 response_type=code&client_id= 组合、回调地址形如 /oauth/callback?code=xxx&state=yyy、参数里有 redirect_uri 且改动后仍然放行_
- 🔴 [PHP 伪协议与 php://filter 过滤器链（convert.iconv 任意文件读取与 RCE）](web/php-filter-chain.md) — _参数值形如 file=index.php 且能读回 PHP 源码、请求里出现 php://filter/convert.base64-encode 字样、源码写 include($_GET['x']) 且参数没有固定前缀、附件给了 php-fpm 或 php.ini 配置，disable_functions 很长_
- 🔴 [Ruby Marshal / Python Marshal / .NET 反序列化（跨语言 gadget）](web/ruby-python-dotnet-deserialization.md) — _Cookie 或参数以 BAh7 开头、数据以 \x04\x08 开头、出现 Marshal.load 或 YAML.load 关键词、响应体是 base64 且解码后为二进制_
- 🔴 [SAML 断言伪造与 XSW（XML Signature Wrapping）攻击](web/saml-xsw-attack.md) — _POST 表单字段名 SAMLResponse、响应体是 base64 的 <samlp:Response>、存在 /SAML/SSO 或 /adfs/ls 端点、断言里有 <ds:Signature> 与 <Assertion ID=_
- 🔴 [SSTI 进阶：无回显盲注探测与 Jinja2 沙箱逃逸完整链](web/ssti-blind-and-sandbox-escape.md) — _提交 {{7*7}} 没有 49 回显，但页面响应正常返回、输入 {{1/0}} 返回 500，正常输入返回 200、模板只在邮件 / PDF / 日志里渲染，前端看不到结果、报错页出现 TemplateRuntimeError 或 UndefinedError_
- 🔴 [Spring4Shell CVE-2022-22965（Spring MVC 参数绑定 RCE）](web/cve-2022-22965-spring4shell.md) — _spring mvc、参数绑定、class.module.classLoader、tomcat 部署_
- 🔴 [Web 缓存投毒与缓存欺骗（Cache Poisoning / Deception）](web/web-cache-poisoning-deception.md) — _响应头出现 X-Cache: HIT 或 cf-cache-status: HIT、响应头里有 Age 且连续请求时数值递增、页面里回显了我们塞进 X-Forwarded-Host 的域名、响应出现 Via: 1.1 varnish 或 X-Varnish_
- 🔴 [文件上传：条件竞争与二次渲染、图片马绕过内容检测](web/upload-race-and-image-polyglot.md) — _上传后文件被立刻删除或改名、上传目录可访问 GET /uploads/xxx.php、提示「上传成功但文件已删除」、图片上传后返回缩略图 URL_

<a id="forensics"></a>
## 取证 Forensics (22)

- 🟢 [Linux 日志取证（syslog / SSH / undo 文件）](forensics/linux-log-forensics.md) — _附件是 var log 目录、题目问谁 ssh 登录了、需要还原 vim 编辑内容、需要看 cron 任务_
- 🟢 [元数据取证（EXIF / XMP / 文档属性溯源）](forensics/exif-metadata.md) — _需要知道照片拍摄地点、需要判断照片是否被编辑、需要找设备型号、元数据里有 GPS_
- 🟢 [文件雕刻与恢复（foremost / binwalk / photorec）](forensics/file-carving.md) — _磁盘镜像里有已删除文件、内存 dump 里有 zip 片段、需要按文件类型批量恢复、分区表损坏_
- 🟢 [流量分析基础（Wireshark 追踪流 / 导出对象 / TCP 重组）](forensics/pcap-basics.md) — _附件是 pcap、需要还原上传的文件、需要找管理员密码、流量包很大_
- 🟡 [TCP 流重组与端口扫描识别](forensics/tcp-reassembly.md) — _流量里有大量 S YN 包、同一源 IP 扫了很多端口、需要判断扫描类型、需要还原一次完整会话_
- 🟡 [USB / 移动存储取证（USBSTOR、挂载记录与文件恢复）](forensics/usb-removable-forensics.md) — _题目问这台电脑插过什么 U 盘、附件是一个 Windows 系统的注册表 hive、题目问文件是从哪个设备拷贝过来的、要求还原 U 盘序列号或者厂家型号_
- 🟡 [Windows 取证（注册表 / EVTX 事件日志）](forensics/registry-and-eventlog.md) — _附件是 NTUSER.DAT 或 SYSTEM、附件是 evtx 日志、题目问谁登录过、需要找 U 盘插拔记录_
- 🟡 [云环境取证（AWS CloudTrail、K8s audit log）](forensics/cloud-log-forensics.md) — _附件是 cloudtrail 的 json gz 日志、题目问哪个 access key 创建了新的 iam 用户、日志里 eventSource 字段重复出现同一个异常服务、要求还原攻击者在云上的完整操作链_
- 🟡 [内存取证（Volatility 2/3 常用插件与 profile 判定）](forensics/memory-forensics-volatility.md) — _附件是内存 dump、文件后缀 raw 或 mem 或 vmem、题目问运行了什么进程、需要从内存里找密码_
- 🟡 [加密流量解密（SSLKEYLOGFILE / HTTPS 分析）](forensics/encrypted-pcap.md) — _流量全是 tls 加密、题目说分析 https 流量、wireshark 显示 cannot decrypt、给了 keys.log_
- 🟡 [数据库取证（SQLite freelist/WAL 恢复删除记录）](forensics/sqlite-forensics.md) — _附件是一个 sqlite3 文件或者没有扩展名的数据库、打开发现表里数据明显变少、同目录下还有 -wal 或 -journal 后缀的文件、题目问被删除的记录内容是什么_
- 🟡 [日志时间线重建（plaso / timesketch / 多源时间归一）](forensics/timeline-reconstruction.md) — _题目要求还原某个时间点到底发生了什么、给了多个来源的日志需要合并成一份时间线、日志时间戳有 utc 和本地时间混用、附件里有 evtx 和 json 和 csv 多种格式_
- 🟡 [浏览器取证（Chrome/Edge History、Cookies、下载与扩展）](forensics/browser-artifacts.md) — _给了用户的 Chrome 或 Edge 用户配置目录、附件里有 History Web Data Cookies 这些没有扩展名的文件、题目问用户最后访问的网站或者下载了什么、要求还原被删除的浏览记录_
- 🟡 [磁盘镜像取证（sleuthkit / autopsy / 分区恢复）](forensics/disk-forensics.md) — _附件是 img 或 dd 镜像、存在多个分区、镜像里有被删除文件、需要从镜像里提取 flag_
- 🟡 [邮件取证（EML/PST 解析、附件提取、收发链路）](forensics/email-forensics.md) — _附件是 eml msg 或者 pst 文件、题目问谁给谁发了邮件、邮件源码里有 base64 和 quoted-printable 混排、要求提取附件里的压缩包_
- 🟡 [隐写取证综合（Aperi'Solve 全流程与批量分析）](forensics/steganalysis-workflow.md) — _给了一大批图片要求逐张找出藏了内容的那张、题目说对所有图片跑一遍隐写分析、单张图 binwalk zsteg steghide 都没有结果、需要判断 steghide 有没有密码或者密码是空_
- 🔴 [NTFS / $MFT 取证（数据流 ADS、时间戳伪造识别）](forensics/ntfs-mft-forensics.md) — _附件是一个 ntfs 分区镜像或者一个 MFT 文件、题目问某个文件什么时候被创建或被删除、要求找出 Alternate Data Stream 里藏的内容、时间戳明显不符合逻辑比如修改早于创建_
- 🔴 [macOS / iOS 取证要点](forensics/macos-ios-forensics.md) — _附件是 dmg 或 sparseimage、附件是 iphone 备份目录、题目要求看 mac 上的记录、需要解 keychain_
- 🔴 [内存取证进阶（malfind/malfind2 进程注入与隐藏进程）](forensics/memory-injection-detection.md) — _题目说某个进程被注入了恶意代码、内存镜像里存在明显不在磁盘上的可执行区域、进程列表里有一个名字很怪的进程、从 pslist 能看到但是从 psscan 看不到或者反过来_
- 🔴 [反取证识别（删除痕迹、时间戳篡改、日志清理）](forensics/anti-forensics-detection.md) — _日志显示事件 id 1102 表示审计日志被清空、用户事件日志中间出现大段时间空洞、文件时间戳被改成 1970 或 2000 年、磁盘上出现大量随机字节的覆盖区域_
- 🔴 [流量中的隐写（ICMP/DNS 隧道与隐蔽信道）](forensics/steganography-in-pcap.md) — _大量 icmp 包 payload 很长、dns 查询域名特别长、一个域名下大量子域、定时定量的心跳包_
- 🔴 [高级协议分析（HTTP/2 与 QUIC 解密）](forensics/http2-and-quic.md) — _流量里有 h2 或 h3 协议、wireshark 显示 encrypted alert、需要解密 TLS1.3、给了 sslkeylog 文件_

<a id="mobile"></a>
## 移动端 Mobile (14)

- 🟢 [APK 静态分析（apktool / jadx 全流程）](mobile/apk-static-analysis.md) — _附件是 .apk、需要看清 AndroidManifest 与权限、需要读 Java/Kotlin 逻辑、smali 里有核心判断_
- 🟢 [移动端 CTF 检查清单（Android / iOS 通用流程）](mobile/mobile-ctf-checklist.md) — _拿到一个 apk/ipa 不知从哪下手、时间紧需要固定套路、静态分析卡住、需要判断要不要脱壳/抓包/动态调试_
- 🟡 [Android SSL Pinning 绕过](mobile/android-ssl-pinning-bypass.md) — _mitmproxy 抓不到 https 流量、代理装了证书仍报 SSLHandshakeException、应用提示网络错误但 http 正常、有 trustmanager / certificate pinner_
- 🟡 [Android 动态调试（jdwp 附加、smali 插桩、动态修改返回值）](mobile/android-dynamic-debugging.md) — _APK 的 AndroidManifest 里 debuggable 为 true、题目说直接连 jdwp 端口调试、要求直接改 smali 让校验函数返回 true、附件给的是可编辑的 apk 源码结构_
- 🟡 [Android 签名校验与完整性校验绕过](mobile/android-signature-check.md) — _重打包后 App 闪退、修改 smali 后校验失败、应用启动即检测签名、有 PackageManager.getPackageInfo 取 signatures_
- 🟡 [Android 网络流量（系统 CA 安装、SSL Pinning 各类实现）](mobile/android-network-intercept.md) — _抓包工具里所有请求都显示 handshake failed 或者连接被重置、需要把 burp 的证书装进系统目录、应用使用了 OkHttp 的 CertificatePinner、应用是 Flutter 或者 Unity 写的抓不到明文_
- 🟡 [Frida Hook 实战（脱壳 / root 检测绕过 / 函数替换）](mobile/frida-hook.md) — _需要在运行时改函数返回值、应用有 root/simulator 检测、需要 dump 内存里的 dex、静态分析看到加密但跑起来能出明文_
- 🟡 [Hook 框架对比（Frida / Xposed / LSPosed / Zygisk）](mobile/hook-frameworks-compare.md) — _题目要求在运行时修改某个方法的行为、应用有反 frida 但是设备已经 root、需要一个全局持久生效的 hook 而不是一次性脚本、题目说用 Xposed 模块绕过某个检测_
- 🟡 [iOS 逆向入门（ptrace 反调试 / class-dump / Frida）](mobile/ios-reverse.md) — _附件是 .ipa 或解密后的 Mach-O、需要在越狱设备上跑、有 LC_ENCRYPTION_INFO 加密段、需要 dump Objective-C 类结构_
- 🟡 [移动端 CTF 真题题型汇总（分类打法与解题路径）](mobile/mobile-ctf-task-types.md) — _比赛里 mobile 分类只有一两道题、拿到 apk 但完全不知道从哪下手、题目描述只有一句请分析这个应用、附件同时给了 apk 和 pcap_
- 🔴 [Android native 逆向（.so 的 IDA 分析、JNI 静态与动态注册）](mobile/android-native-jni-reverse.md) — _lib 目录下有 libnative.so 或 libcore.so、Java 层方法声明为 native 没有任何实现、关键算法都在 native 层实现、用 jadx 搜索 System.loadLibrary 发现加载了多个 so_
- 🔴 [Android 加固脱壳（FART / frida-dexdump / FRIDA-DEXDump 全量导出）](mobile/android-unpacking-fart.md) — _apk 里 classes.dex 只有几百 KB 但程序功能很多、用 jadx 打开只能看到壳代码和一堆 Application 子类、题目说 APK 经过某加固厂商处理、运行时会释放真正的 dex_
- 🔴 [Android 反调试高级（ptrace、/proc 检测、反 Frida）](mobile/android-antidebug-advanced.md) — _附加调试器后应用直接退出或者黑屏、程序在启动时读取 /proc/self/status、so 里有 ptrace 调用和 PTRACE_TRACEME、检测到了 frida 的线程名或者 27042 端口_
- 🔴 [iOS 进阶（Mach-O、dyld 注入、LLDB 调试与砸壳）](mobile/ios-macho-dyld-lldb.md) — _附件是一个 Mach-O 二进制或者 IPA、题目说这是砸壳后的 ipa 可以直接反编译、需要注入 dylib 绕过某个校验、应用是 Swift 写的符号表被 strip 了_

<a id="blockchain"></a>
## 区块链 Blockchain (6)

- 🟢 [Solidity 整数溢出 / 下溢（SWC-101）](blockchain/solidity-integer-overflow.md) — _solidity 0.7 及以下、SafeMath、uint256 减法、余额减到负数_
- 🟡 [EVM 存储槽位读取（private 变量 / 任意写）](blockchain/evm-storage-slot.md) — _private 变量、存储在 slot、isSolved 读 storage、数组和 mapping_
- 🟡 [Solana CTF 常见点（signer 校验缺失 / PDA / owner 校验）](blockchain/solana-ctf.md) — _solana、anchor、sbf、账户没有 is_signer_
- 🟡 [Solidity 权限与初始化漏洞（SWC-105/106/108/118）](blockchain/solidity-access-control.md) — _构造函数没有权限、onlyOwner 未加、初始化函数 initializer、initialize 可重复调用_
- 🟡 [Solidity 重入攻击（Reentrancy / SWC-107）](blockchain/solidity-reentrancy.md) — _合约有 withdraw、先转账后扣余额、call.value、fallback 函数_
- 🟡 [智能合约常见 CVE 与 SWC 缺陷汇总](blockchain/solidity-cve-collection.md) — _swc 编号、漏洞分类、审计题、需要判断漏洞类型_

<a id="hardware"></a>
## 硬件 Hardware (14)

- 🟡 [CAN 总线攻击（车载/工控报文分析）](hardware/can-bus.md) — _附件是 can 报文日志、题目提到车载或工控总线、需要还原 can 帧里的数据、有大量 id 相同的帧_
- 🟡 [SPI Flash / EEPROM 读写与固件提取（CH341A + flashrom）](hardware/spi-flash-eeprom.md) — _板子上有一颗 8 脚的小芯片型号是 W25Q 或者 MX25L、题目说固件在 flash 里需要读出来、附件是 .bin 但是开头是 ff ff ff 或者一大片 00、要求提取路由器或摄像头的固件镜像_
- 🟡 [UART / JTAG / SWD 接口识别与调试](hardware/uart-jtag-swd.md) — _板子上有 4 针排针、需要找调试接口、串口没有输出、需要连 jtag 读 flash_
- 🟡 [固件分析（binwalk 提取 / 文件系统 / 服务漏洞）](hardware/firmware-analysis.md) — _附件是固件 bin、binwalk 扫描出多个段、需要找硬编码密码、固件是 ubi 或 squashfs_
- 🟡 [嵌入式 Linux（串口登录、U-Boot 中断、rootfs 提取）](hardware/embedded-linux-boot.md) — _板子上有 4 针 UART 排针标注 TX RX GND VCC、115200 8N1 串口能刷出启动日志、启动时提示按任意键进入 U-Boot 控制台、题目要求拿到 rootfs 里的 flag_
- 🟡 [工控协议（Modbus 与 S7comm 报文分析）](hardware/plc-protocol-analysis.md) — _抓包里有 502 或 102 端口、题目说这是工控网络流量、需要还原 PLC 寄存器被写入的值、报文里出现协议 ID 0x32_
- 🟡 [逻辑分析仪（UART/SPI/I2C 波形解码）](hardware/logic-analyzer.md) — _给了一段波形文件、附件是 .sal 或 .sr 或 .logicdata、题目说从总线抓了数据、需要还原串口输出_
- 🔴 [JTAG 实战（OpenOCD 配置、halt、dump 与断点）](hardware/jtag-openocd-workflow.md) — _目标板有 20 针 JTAG 排针或者 TMS TCK TDI TDO 丝印、附件是一块 ARM 开发板或者 Cortex-M 芯片、题目要求暂停 CPU 并读出 flash、需要用 gdb 连上目标调试_
- 🔴 [RFID / NFC / 蓝牙 BLE 抓包与攻击](hardware/rf-iot.md) — _题目给出门禁卡数据、需要解密 mifare classic、需要嗅探 ble 通信、附件是 nfc dump 文件_
- 🔴 [侧信道分析（时序 / 功耗 / 缓存）](hardware/side-channel.md) — _题目提供多次运行的时间、需要比较密码比较耗时、需要从功耗曲线猜密钥、题面提到 side channel_
- 🔴 [故障注入（电压毛刺 glitch、时钟毛刺与绕过比对）](hardware/fault-injection-glitch.md) — _题目要求通过让芯片在特定时刻出错来跳过校验、板子上有一颗 LGT8F 或 STM32 且需要解出密钥、提示提到 glitch 或 fault 或 crowbar、附件是 chipwhisperer 的 notebook_
- 🔴 [无线电进阶（SDR、ASK/FSK 解码、sigidwiki 识别）](hardware/sdr-signal-decoding.md) — _附件是一个 iq 采样文件或者 wav 里录了射频声音、题目给的频率是 433.92MHz 或者 315MHz、需要在频谱图里找出一段周期性突发信号、提示说这是 ask 或者 ook 调制_
- 🔴 [硬件 CTF 综合题解思路（从板子到 flag 的全链路）](hardware/hardware-ctf-methodology.md) — _题目给了一块板子的照片或者实物、附件是一个固件或者一串串口日志、题目没有任何提示只有一句请拿到 flag、需要从板上找出测试点然后接到串口_
- 🔴 [芯片安全（安全启动链、TrustZone 攻击面与密钥提取）](hardware/secure-boot-trustzone.md) — _题目说设备有安全启动需要绕过、芯片是 ARM TrustZone 架构分正常世界和安全世界、要求从 TEE 里提取密钥或者通信凭证、固件带签名校验且签名被硬编码在 rom 里_

<a id="osint"></a>
## 情报 OSINT (12)

- 🟢 [OSINT 完整检查清单（从零到证据链）](osint/osint-checklist.md) — _题目只给一个目标名、不知道从哪开始查、需要写调查报告、已经查到一些信息需要补全_
- 🟢 [OSINT 工具集与语法（Google Dork）](osint/osint-toolsets.md) — _题目只给一个关键词、需要找特定文件、需要找某个站点的备份文件、需要搜特定格式的文档_
- 🟢 [图片反查与 AI 图像指纹](osint/osint-image-reverse.md) — _题目给一张图问来源、需要找出处或原图、需要判断是否 AI 生成、需要找被裁切的原图_
- 🟢 [域名 / IP / 证书溯源（FOFA、Shodan、crt.sh）](osint/osint-domain-infra.md) — _题目给了一个域名、需要找同一实体的其他资产、需要找子域名、需要证书信息_
- 🟡 [OSINT 自动化（脚本化收集与结果落盘）](osint/osint-automation.md) — _题目要求对一个域名做全面信息收集、需要快速把几百个子域名的存活情况摸清楚、要批量查询多个 whois 和 dns 记录、题目分在 osint 但目标明确给了范围_
- 🟡 [人员溯源（LinkedIn/GitHub/邮箱信息聚合）](osint/person-tracing.md) — _题目给出了一个用户名要求找他所有的社交账号、给了邮箱地址要求推断真名或者公司、题目目标是一个开发者的 github 主页、要求从招聘网站或者简历推断学历经历_
- 🟡 [反 OSINT（出题与防守视角的隐私保护）](osint/anti-osint-privacy.md) — _题目要求设计一个不易被溯源的信息暴露方案、给出一张截图问会泄露哪些位置和身份信息、要求找出图片中需要打码或清除的元数据、题目是防守视角的隐私泄露审计_
- 🟡 [地理定位技巧（阴影 / 路标 / 语言 / 星象）](osint/osint-geolocation.md) — _题目给一张街景照片问在哪、需要根据照片定位坐标、照片有电线杆和路牌、照片有云或太阳_
- 🟡 [泄漏数据检索（合法 CTF 语境下的数据聚合与验证）](osint/leaked-data-search.md) — _题目要求判断某个邮箱是否出现在公开泄漏事件里、附件里有一份包含用户名和邮箱的 csv 转储、题目问某个密码是否曾泄漏过、给了哈希值要求反查对应的明文_
- 🟡 [社媒溯源（账号关联 / 用户名枚举 / 图片反查）](osint/osint-social-media.md) — _题目给了一个用户名、需要找到同一个人的其他账号、需要找作者主页、需要还原发布历史_
- 🔴 [图像地理定位进阶（卫星图比对、街景与超分辨率线索）](osint/geolocation-advanced.md) — _给了一张航拍图或者卫星截图要求定位、图片来自某个地图软件的截图有明显缩放按钮、需要根据阴影方向推断太阳方位和时间、图里有铁路道口或者特殊路牌_
- 🔴 [时间线交叉验证（多源信息配置与矛盾检测）](osint/timeline-crosscheck.md) — _题目给出了多张照片和几段对话要求判断先后、需要还原某个人在某个时间段的行踪、信息之间有时间冲突需要判断哪条是伪造的、题目给了时区不同地区的截图_

<a id="ai"></a>
## AI 安全 (12)

- 🟢 [AI CTF 检查清单（大模型题型通用流程）](ai/ai-ctf-checklist.md) — _题目属于 ai 类别不知道从哪下手、给了一个模型或聊天接口、需要构造 prompt 而不是代码、时间不够要按套路走_
- 🟡 [AI 编码题打法（模型辅助逆向与找 bug 的实战流程）](ai/ai-coding-reverse.md) — _题目给了大量混淆后的代码要求快速读懂、题目要求在有限时间内找到二进制里的漏洞点、附件是一个巨大的二进制或者源码树、提示说可以用 AI 辅助分析_
- 🟡 [LLM 越狱（常见套路与防护）](ai/llm-jailbreak.md) — _题目要求模型输出被拒答的内容、需要绕过对齐策略、会先被安全过滤器拦截、需要多轮诱导_
- 🟡 [提示词注入（直接 / 间接）](ai/prompt-injection.md) — _题目给了个能对话的 llm 接口、需要让模型输出系统提示词、用户输入被拼进 prompt、网页或文档内容会被模型读取_
- 🟡 [系统提示词泄露实战技巧集（提取、变形、复现）](ai/system-prompt-leak.md) — _题目要求在聊天界面里获取隐藏的系统提示词、给了模型接口但系统提示里有 flag、要求还原模型的开场白或者约束条件、题目说明系统提示中包含敏感信息需要提取_
- 🔴 [Agent 工具滥用（LLM 工具调用 / 过度代理）](ai/llm-tool-abuse.md) — _题目给了一个能调用工具的 agent、能读文件或访问网络、需要让它执行命令、需要组合多个工具_
- 🔴 [Agent 越权与工具链攻击（实际利用链拆解）](ai/agent-privilege-escalation.md) — _题目给了一个能调用工具的智能体、工具列表里有文件读写和网络请求、要求让 agent 去读取它本来没权限访问的文件、MCP server 的描述里藏了指令_
- 🔴 [RAG 知识库投毒（检索增强生成攻击面）](ai/rag-poisoning.md) — _题目给了个基于文档的问答机器人、有上传/编辑文档的入口、需要让模型回答特定内容、需要从知识库里钓出 flag_
- 🔴 [后门攻击与投毒（Backdoor / Trojan / 触发词）](ai/backdoor-and-poisoning.md) — _题目给了一个已经训练好的模型需要找出隐藏后门、模型在正常输入上表现正常但特定输入会输出错误标签、训练数据里有一小部分被污染需要找出来、需要构造一个触发词让模型输出指定结果_
- 🔴 [多模态攻击（图片/语音提示注入与跨模态越狱）](ai/multimodal-injection.md) — _题目要求把提示词隐藏进图片里、给了一个视觉语言模型要求让它说出指定内容、图片里用白字白底或者极低对比度藏了文字、题目提供了语音文件要求让语音助手执行指令_
- 🔴 [对抗样本基础（FGSM / PGD / 迁移攻击）](ai/adversarial-example.md) — _题目给了一个图像分类模型、需要让模型判错、需要加不可见扰动、需要提取特征或权重_
- 🔴 [模型窃取与成员推理（Model Extraction / Membership Inference）](ai/model-extraction-membership.md) — _题目给了一个只返回预测结果的模型接口、要求还原模型的参数或者结构、问某个样本是否在训练集里、给了预测接口和一批候选样本要求判断训练集成员_

## 识别信号速查

看到题面里出现这些词，直接去对应条目：

- **e=3** → RSA 低加密指数广播攻击（Håstad）、RSA 小公钥指数攻击（小明文开方 / Coppersmith）
- **padding error** → AES-CBC 字节翻转 / 逐字节解密（Padding Oracle）、RSA Padding Oracle 攻击（Bleichenbacher / PKCS#1 v1.5）
- **附件是 .apk** → APK 静态分析（apktool / jadx 全流程）、Android APK 逆向与 native so 分析
- **$gt** → NoSQL 注入（MongoDB 操作符注入）
- **$ne** → NoSQL 注入（MongoDB 操作符注入）
- **../** → 文件包含 LFI/RFI（php://filter / 日志包含）
- **/actuator** → Jolokia / iBatis 等常见 Java 组件利用
- **/proc/1/cgroup 里出现 docker 或 kubectl 字样** → Docker / K8s 场景下的 Web 逃逸（docker.sock 挂载、runc 漏洞）
- **1.2.x 版本** → Fastjson 反序列化（autoType / @type）
- **10.0 分** → CVE-2024-3400 PAN-OS GlobalProtect 命令注入（10.0 分）
- **115200 8N1 串口能刷出启动日志** → 嵌入式 Linux（串口登录、U-Boot 中断、rootfs 提取）
- **16 字节一块** → AES-ECB 分组相等分析（ECB Penguin）
- **169.254.169.254** → SSRF 服务端请求伪造（内网穿透 / gopher 打 Redis / 云元数据）
- **2.34 后 __free_hook 找不到** → __malloc_hook / __free_hook 与 2.34+ 替代方案
- **32 位 i386 且无 PIE 的老题** → ret2dlresolve —— 无 libc 泄露时伪造动态链接解析结构拿 system
- **32 位附件** → 基础栈溢出 ret2text / ret2shellcode
- **403** → SQL 注入 WAF 绕过技巧集
- **403 只能读文件** → 文件包含 LFI/RFI（php://filter / 日志包含）
- **500 错误** → Shiro-550 / Shiro-721（rememberMe 反序列化）
- **5005 端口** → JNDI 注入 + JDWP / RMI 利用
- **5050 端口** → Jolokia / iBatis 等常见 Java 组件利用
- **5077 端口** → Jolokia / iBatis 等常见 Java 组件利用
- **624 个输出** → MT19937 随机数破译（untemper）
- **64 位下栈上是寄存器转存区** → 格式化字符串进阶 —— %hhn 分字节写、大数值写与多目标改写链
- **64 位小体积二进制** → ret2csu 与 gadget 搜索（ROPgadget / ropper）
- **7z 提示 CRC 错误** → ZIP 压缩包技巧（伪加密/明文攻击/CRC 爆破）
- **8000 端口是 rmi** → JNDI 注入 + JDWP / RMI 利用
- **9068** → CVE-2024-4577 PHP-CGI Windows 参数注入 RCE
- **<!--#exec cmd** → SSI / Servlet 冷门注入点（含 JSP/EL 注入）
- **APK 的 AndroidManifest 里 debuggable 为 true** → Android 动态调试（jdwp 附加、smali 插桩、动态修改返回值）
- **APK 的 lib 目录下有 libapp.so 且体积超过 5MB** → Flutter / Dart AOT 逆向（libapp.so 与 Blutter）
- **APK 里有 libil2cpp.so 且伴随 global-metadata.dat** → Unity il2cpp 进阶（global-metadata.dat 还原与 Il2CppDumper 全流程）
- **AndroidManifest 里 application 指向陌生的类名** → Android 加固脱壳（FART / frida-dexdump / FRIDA-DEXDump 全量导出）
- **Apache SSI** → SSI / Servlet 冷门注入点（含 JSP/EL 注入）
- **Apache Shiro** → Shiro-550 / Shiro-721（rememberMe 反序列化）
- **Cookie rememberMe** → Shiro-550 / Shiro-721（rememberMe 反序列化）
- **Cookie 或参数以 BAh7 开头** → Ruby Marshal / Python Marshal / .NET 反序列化（跨语言 gadget）
- **Cookies 里加密的 value 以 v10 开头** → 浏览器取证（Chrome/Edge History、Cookies、下载与扩展）
- **Dockerfile 里写了 ubuntu:20.04** → checksec 与保护机制判读速查
- **EXIF 里有奇怪注释** → JPG 图片隐写（DCT/outguess/steghide/EXIF）
- **Full RELRO 无 GOT 可改** → FSOP 与 _IO_FILE 伪造 vtable（House of Orange / 2.34+）
- **GET /graphql?query={__typename} 返回 Query 类型名** → GraphQL 攻击（introspection、别名批量绕过限流、字段建议泄露、注入）
- **GIF 每帧延迟大量为 0** → BMP/GIF/TIFF 隐写进阶（调色板/帧延迟/扩展标签）
- **IDA 反编译报 "call analysis failed" 或大量 jmp 到未知块** → 反编译失败时的动态调优（混淆对抗与断点定位关键比较）
- **IDA 反编译报 call analysis failed** → 花指令与控制流平坦化还原（含 IDA 脚本）
- **IDA 的 F5 结果完全不正确** → 反编译失败时的动态调优（混淆对抗与断点定位关键比较）
- **IEND 之后还有数据** → PNG 图片隐写排查（binwalk/zsteg/CRC 宽高/LSB/IDAT）
- **IdP 元数据文件出现了证书** → SAML 断言伪造与 XSW（XML Signature Wrapping）攻击
- **Java 层方法声明为 native 没有任何实现** → Android native 逆向（.so 的 IDA 分析、JNI 静态与动态注册）
- **Java 层逻辑很少** → Android APK 逆向与 native so 分析
- **Linux 下能直接解压** → ZIP 压缩包技巧（伪加密/明文攻击/CRC 爆破）
- **MAC 可被伪造** → 哈希长度扩展攻击（Hash Length Extension）
- **MCP server 的描述里藏了指令** → Agent 越权与工具链攻击（实际利用链拆解）
- **NX 关闭** → 基础栈溢出 ret2text / ret2shellcode
- **NX 开启且无 win 函数** → ret2libc —— libc 基址泄露与 system("/bin/sh")
- **Nginx 版本较老，PHP 用 header() 拼接 $_GET** → CRLF 注入与 HTTP 响应拆分（Header 注入、Set-Cookie 劫持）
- **OpenOCD 报无法识别目标芯片** → JTAG 实战（OpenOCD 配置、halt、dump 与断点）
- **PC 游戏有 GameAssembly.dll 与 global-metadata.dat** → Unity il2cpp 进阶（global-metadata.dat 还原与 Il2CppDumper 全流程）
- **PIE 关闭** → 基础栈溢出 ret2text / ret2shellcode
- **PIE 开启但目标与返回地址同页** → partial overwrite 与受限单字节 / OOB 写
- **PKCS#1 v1.5** → RSA Padding Oracle 攻击（Bleichenbacher / PKCS#1 v1.5）
- **POST 表单字段名 SAMLResponse** → SAML 断言伪造与 XSW（XML Signature Wrapping）攻击
- **ROPgadget 只搜到 ret 结尾的片段** → ret2csu 与 gadget 搜索（ROPgadget / ropper）
- **SafeMath** → Solidity 整数溢出 / 下溢（SWC-101）
- **TIFF 里有一堆没见过的 tag** → BMP/GIF/TIFF 隐写进阶（调色板/帧延迟/扩展标签）
- **TemplatesImpl** → Fastjson 反序列化（autoType / @type）
- **UA 被记录** → Log4Shell CVE-2021-44228（JNDI 注入）
- **UAF show 能读出乱码地址** → unsorted bin 泄露 libc（2.23 ~ 2.35 通用）
- **URL 里出现 response_type=code&client_id= 组合** → OAuth 2.0 / OIDC 与 SSO 绕过（redirect_uri、state、账号接管）
- **Unity 游戏里有 GameAssembly.dll 与 global-metadata.dat** → .NET / C# 逆向（dnSpyEx / ILSpy）与 Unity il2cpp
- **Vary 头只写了 User-Agent 或干脆没有** → Web 缓存投毒与缓存欺骗（Cache Poisoning / Deception）
- **Windows 上没有 Linux 工具** → 工具矩阵与 WSL 常用命令（CyberChef/StegSolve/hex 工具箱）
- **__destruct** → PHP 反序列化（__wakeup / __destruct / POP 链）
- **__free_hook 已不可用** → FSOP 与 _IO_FILE 伪造 vtable（House of Orange / 2.34+）
- **__free_hook 找不到** → glibc 2.27 ~ 2.41 版本差异速查（Pwn 视角）
- **__proto__** → JS 原型链污染（Prototype Pollution）
- **__wakeup** → PHP 反序列化（__wakeup / __destruct / POP 链）
- **a b m 参数** → 线性同余随机数预测（LCG）
- **admin bot** → XSS 跨站脚本（含 CSP 绕过）
- **admin 权限被加密** → AES-CBC 字节翻转 / 逐字节解密（Padding Oracle）
- **alg none** → JWT 伪造（none 算法 / 密钥爆破 / RS256→HS256）
- **allow_url_include** → CVE-2024-4577 PHP-CGI Windows 参数注入 RCE
- **anchor** → Solana CTF 常见点（signer 校验缺失 / PDA / owner 校验）
- **angr 跑不动但逻辑是直线代码** → z3 约束求解还原算法
- **apk 里 classes.dex 只有几百 KB 但程序功能很多** → Android 加固脱壳（FART / frida-dexdump / FRIDA-DEXDump 全量导出）
- **application/json 登录** → NoSQL 注入（MongoDB 操作符注入）
- **assembly-CSharp.dll 只有 3KB** → Unity il2cpp 进阶（global-metadata.dat 还原与 Il2CppDumper 全流程）
- **assets 目录下大量 .lua 但是二进制** → LuaJIT 字节码与手游脚本逆向（lj_bc 还原）
- **assets 里没有 Flutter 业务代码** → Flutter / Dart AOT 逆向（libapp.so 与 Blutter）
- **atbash** → 古典密码（Atbash / 凯撒 / 维吉尼亚 / 仿射 / 巴利克）
- **authorization bearer** → JWT 伪造（none 算法 / 密钥爆破 / RS256→HS256）
- **autoType** → Fastjson 反序列化（autoType / @type）
- **bacon** → 古典密码（Atbash / 凯撒 / 维吉尼亚 / 仿射 / 巴利克）
- **base64 收到 rO0AB 开头** → Java 反序列化（CC 链 / ysoserial / JNDI）
- **binwalk 分离不完整** → 文件雕刻与恢复（foremost / binwalk / photorec）
- **binwalk 扫描出多个段** → 固件分析（binwalk 提取 / 文件系统 / 服务漏洞）
- **binwalk 报错** → 工具矩阵与 WSL 常用命令（CyberChef/StegSolve/hex 工具箱）
- **binwalk 能看出 SquashFS 或 CramFS 文件系统** → 固件 / IoT 逆向（固件镜像解包与嵌入式二进制分析）
- **blind xxe** → XXE 外部实体注入（含 Blind OOB / SSRF 组合）
- **bm 算法** → LFSR 关联攻击 / BM 算法（线性反馈移位寄存器）
- **buf** → 栈迁移（leave; ret）与栈劫持
- **call.value** → Solidity 重入攻击（Reentrancy / SWC-107）
- **cbc 模式** → AES-CBC 字节翻转 / 逐字节解密（Padding Oracle）
- **cgi 模式** → CVE-2024-4577 PHP-CGI Windows 参数注入 RCE
- **checksec 显示 Canary found** → Canary 绕过四种打法（泄露 / 爆破 / __stack_chk_fail / TLS）
- **checksec 显示 PIE enabled** → PIE 绕过 —— 部分覆盖与信息泄露
- **checksec 显示 Partial RELRO 或 No RELRO** → ret2dlresolve —— 无 libc 泄露时伪造动态链接解析结构拿 system
- **checksec 显示 seccomp 沙箱已启用且有 BPF 规则** → seccomp 高级绕过 —— x32 ABI 混淆、openat2 与 TIOCSTI
- **chunk 大小大于 0x408 会跳过 tcache** → unsorted bin 泄露 libc（2.23 ~ 2.35 通用）
- **chunk 的 size 低字节是 0x21 或 0x31 这类小值** → House of Einherjar —— 单 null 字节覆盖 size 造成堆重叠
- **ci_job_token** → CVE-2024-6385 GitLab 以任意用户身份运行 Pipeline
- **class 定义一串** → PHP 反序列化（__wakeup / __destruct / POP 链）
- **class.module.classLoader** → Spring4Shell CVE-2022-22965（Spring MVC 参数绑定 RCE）
- **commit_creds 出现在 System.map** → Linux 内核 pwn 入门（modprobe_path / commit_creds）
- **commons-collections 依赖** → Java 反序列化（CC 链 / ysoserial / JNDI）
- **config 合并** → JS 原型链污染（Prototype Pollution）
- **constructor.prototype** → JS 原型链污染（Prototype Pollution）
- **cookie 值很长以 base64 结尾** → Shiro-550 / Shiro-721（rememberMe 反序列化）
- **cookie 是 flag** → XSS 跨站脚本（含 CSP 绕过）
- **cookie 里是 jwt** → JWT 伪造（none 算法 / 密钥爆破 / RS256→HS256）
- **cookie 里是序列化数据** → PHP 反序列化（__wakeup / __destruct / POP 链）
- **csp 响应头** → XSS 跨站脚本（含 CSP 绕过）
- **cve 区块链** → 智能合约常见 CVE 与 SWC 缺陷汇总
- **cve-2016-4437** → Shiro-550 / Shiro-721（rememberMe 反序列化）
- **cve-2017-18349** → Fastjson 反序列化（autoType / @type）
- **cve-2021-44228** → Log4Shell CVE-2021-44228（JNDI 注入）
- **cve-2022-22965** → Spring4Shell CVE-2022-22965（Spring MVC 参数绑定 RCE）
- **cve-2024-21626** → CVE-2024-21626 runc 容器逃逸（Leaky Vessels）
- **cve-2024-3400** → CVE-2024-3400 PAN-OS GlobalProtect 命令注入（10.0 分）
- **cve-2024-4577** → CVE-2024-4577 PHP-CGI Windows 参数注入 RCE
- **cve-2024-6385** → CVE-2024-6385 GitLab 以任意用户身份运行 Pipeline
- **d 很多位已知** → ECDSA/EdDSA 随机数重用与偏置 nonce（格攻击）
- **d 很小** → RSA 维纳攻击（d 过小 / e 过大）
- **delegatecall** → Solidity 权限与初始化漏洞（SWC-105/106/108/118）
- **direct transfer** → CVE-2024-6385 GitLab 以任意用户身份运行 Pipeline
- **dns 查询域名特别长** → 流量中的隐写（ICMP/DNS 隧道与隐蔽信道）
- **docker 容器** → CVE-2024-21626 runc 容器逃逸（Leaky Vessels）
- **doctype** → XXE 外部实体注入（含 Blind OOB / SSRF 组合）
- **docx xlsx 解析** → XXE 外部实体注入（含 Blind OOB / SSRF 组合）
- **double free 未检测** → tcache poisoning 与 safe-linking 绕过（2.26 ~ 2.41）
- **double free 未被检测** → Fastbin attack —— fastbin dup / into stack / house of spirit
- **dp dq 泄漏** → RSA dp 泄露攻击
- **dq 或 dp** → RSA dp 泄露攻击
- **e d p q 部分已知** → RSA dp 泄露攻击
- **e 不同** → 弱 RSA 共模攻击
- **e 和 n 位数差不多** → RSA 维纳攻击（d 过小 / e 过大）
- **e 很小** → RSA 小公钥指数攻击（小明文开方 / Coppersmith）
- **e 很小且签名满足 0 的填充** → RSA CRT 故障注入（Bellcore）与签名故障恢复 n
- **e 有十几位十六进制** → RSA 维纳攻击（d 过小 / e 过大）
- **e 比 n 还大** → RSA 维纳攻击（d 过小 / e 过大）
- **e 相同且很小** → RSA 低加密指数广播攻击（Håstad）
- **e 非常大** → RSA 维纳攻击（d 过小 / e 过大）
- **e2)=1** → 弱 RSA 共模攻击
- **e=5 或 e=17** → RSA 小公钥指数攻击（小明文开方 / Coppersmith）
- **ecb oracle** → AES-ECB 分组相等分析（ECB Penguin）
- **ecb 模式** → AES-ECB 分组相等分析（ECB Penguin）
- **ecc** → ECC 小阶 / 无效曲线攻击（Invalid Curve / Small Subgroup）
- **ecdh** → ECC 小阶 / 无效曲线攻击（Invalid Curve / Small Subgroup）
- **edit 长度不校验** → UAF 与堆溢出综述（题型 / 原语 / 利用路线图）
- **ejs pug 模板** → JS 原型链污染（Prototype Pollution）
- **el 注入** → SSI / Servlet 冷门注入点（含 JSP/EL 注入）
- **eth 余额** → Solidity 重入攻击（Reentrancy / SWC-107）
- **eval 在魔术方法里** → PHP 反序列化（__wakeup / __destruct / POP 链）
- **eval 黑名单** → Python pickle 反序列化 & pyjail 逃逸
- **execve 被拒绝返回-EPERM** → seccomp 沙箱下的 ORW（open/read/write）与沙箱绕过
- **eyJhbGciOi** → JWT 伪造（none 算法 / 密钥爆破 / RS256→HS256）
- **fallback 函数** → Solidity 重入攻击（Reentrancy / SWC-107）
- **fastjson 依赖** → Fastjson 反序列化（autoType / @type）
- **file 参数** → 文件包含 LFI/RFI（php://filter / 日志包含）
- **file 命令识别不出类型或者识别成 data** → 文件修复与损坏识别（手工重建头部、CRC 重算）
- **file 显示 ARM aarch64 或 arm 32 位小端** → ARM / AArch64 pwn 入门 —— 交叉编译、ARM 汇编要点与 ROP 构造
- **file_exists** → PHAR 反序列化（phar:// 触发）
- **file_get_contents** → PHAR 反序列化（phar:// 触发）
- **file_put_contents** → PHP 反序列化（__wakeup / __destruct / POP 链）
- **flag 很短** → RSA 小公钥指数攻击（小明文开方 / Coppersmith）
- **flag 藏在一串字母里** → 古典密码（Atbash / 凯撒 / 维吉尼亚 / 仿射 / 巴利克）
- **forced3w** → Jolokia / iBatis 等常见 Java 组件利用
- **fork 服务且每次连接重启** → Canary 绕过四种打法（泄露 / 爆破 / __stack_chk_fail / TLS）
- **free 之后还能 edit (UAF)** → tcache poisoning 与 safe-linking 绕过（2.26 ~ 2.41）
- **free 参数来自全局变量而不是固定索引** → House of Spirit 与 fastbin dup —— 区别、选择与分工
- **free 后 chunk 头部没有任何 size 字段** → musl libc pwn —— mallocng 的 meta/group 结构差异与利用
- **free 后希望和前方伪造块合并** → House of Einherjar —— 单 null 字节覆盖 size 造成堆重叠
- **free 后指针未清** → UAF 与堆溢出综述（题型 / 原语 / 利用路线图）
- **fs:0x28 出现** → Canary 绕过四种打法（泄露 / 爆破 / __stack_chk_fail / TLS）
- **gadget chain** → Java 反序列化（CC 链 / ysoserial / JNDI）
- **gcd(e1** → 弱 RSA 共模攻击
- **gets/read 读入 buf 且长度超限** → 基础栈溢出 ret2text / ret2shellcode
- **gitlab 实例** → CVE-2024-6385 GitLab 以任意用户身份运行 Pipeline
- **glibc 2.24 或 2.35** → FSOP 与 _IO_FILE 伪造 vtable（House of Orange / 2.34+）
- **glibc 2.29 到 2.31 的题目** → tcache stashing unlink attack —— small bin 遍历 + tcache 链构造
- **glibc 2.31 及以上 unsorted attack 失效** → large bin attack 与 House of Force / House of Lore
- **glibc 版本 2.35 及以上** → glibc 2.34+ 的 IO 结构进阶 —— _IO_wfile / House of Kiwi / House of Cat
- **globalprotect** → CVE-2024-3400 PAN-OS GlobalProtect 命令注入（10.0 分）
- **gopher 协议** → SSRF 服务端请求伪造（内网穿透 / gopher 打 Redis / 云元数据）
- **hex 里每隔一个字节是 00 或者 0x00 后置** → 冷门编码家族（UTF-7/16、EBCDIC、rot47、base91/92、QP、Punycode）
- **hidden number problem** → 格攻击入门（LLL / Coppersmith 载体构造）
- **host 参数** → 命令注入与绕过
- **ibatis 报错** → Jolokia / iBatis 等常见 Java 组件利用
- **id=1 页面回显不同** → SQL 注入基础（联合查询 / 盲注 / 时间盲注 + sqlmap）
- **include** → PHAR 反序列化（phar:// 触发）
