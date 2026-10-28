---
title: 芯片安全（安全启动链、TrustZone 攻击面与密钥提取）
category: hardware
tags: [secure-boot, trustzone, tee, key-extraction, bootrom, attestation]
signals: [题目说设备有安全启动需要绕过, 芯片是 ARM TrustZone 架构分正常世界和安全世界, 要求从 TEE 里提取密钥或者通信凭证, 固件带签名校验且签名被硬编码在 rom 里, 提示提到 OP-TEE 或者 TrustZone-M, 题目给了安全启动的日志显示 signature verification failed]
difficulty: hard
source: "ARM TrustZone 架构文档 / OP-TEE 文档 / 安全启动公开研究（TrustZone-M(eh) 等）"
tools: [binwalk, ghidra, frida, op-tee, arm-trusted-firmware, chipwhisperer, uart]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 题目描述"设备的固件被签名保护，无法刷入修改版"。
- 启动日志里能看到 `Verified Boot`、`signature verification failed`、`AVB`、`secure boot enabled`。
- 芯片型号是带 TrustZone 的（Cortex-A `TrustZone-A`、Cortex-M23/M33 `TrustZone-M`）。
- 要求从"安全世界"或"TEE"里读一段密钥。
- 附件含 `tee.bin`、`tz.mbn`、`trusted-firmware-a` 之类的镜像。
- OTP/eFuse 的读取被禁止（读出来全是 0）。

## 二、原理

**安全启动 = 不可变的信任根逐级验证下一级镜像的签名。**

```
BootROM(固化,不可改) -> 一级引导(signed) -> U-Boot/TF-A(signed) -> Kernel(signed) -> Rootfs(dm-verity)
```

**信任根在 BootROM（掩膜 ROM）里**，公钥的哈希通常烧在 eFuse/OTP 中，**只读不可改**。所以"改固件让签名通过"在密码学上不可行；攻击面在于：

1. **BootROM 的解析漏洞**：镜像格式解析（长度字段、偏移、溢出）——"undocumented commands"在 BootROM 的调试口上存在。
2. **回滚绕过**：把旧版本但签名合法的固件刷回（降级攻击），再利用旧版已知漏洞。
3. **故障注入**：在验签比较的那一步做电压/时钟毛刺，让"签名不匹配"的分支被判为匹配（见 `fault-injection-glitch`）。
4. **TrustZone 的攻击面**：
   - NS（Normal World）能访问的共享内存会造成 TEE 数据泄漏；
   - TEE 的 SMC 处理函数（`OPTEE_SMC_*`）输入校验不全，可直接读 TEE 内存；
   - 调试口（JTAG）在 TEE 启动后可关闭，但关闭前可 dump；
   - 缓存侧信道（`Prime+Probe`）推 TEE 的访问模式。
5. **密钥提取的位置**：eFuse 不可读，但**运行时密钥会驻留在内存**，所以"从 RAM 里 dump"比"读 eFuse"更实际。

## 三、操作步骤

1. **确认信任根与 OTP**：读芯片数据手册，看 eFuse 布局；尝试读取 OTP 区域（有些芯片在调试口下可读）。
2. **拆镜像**：`binwalk`/`unblob` 切出各阶段；`strings` 找 `RSA`、`SHA256`、公钥 moduli。
3. **找验签点**：Ghidra 定位 `memcmp`/公钥运算，确认比较的是哈希还是签名本身。
4. **找可绕过的解析点**：看 BootROM 的镜像头解析（长度、版本号），是否有"版本 0 表示跳过校验"的逻辑。
5. **降级测试**：找一份旧版签名合法固件，尝试刷入（看是否被 anti-rollback 拒绝）。
6. **运行时取密钥**：挂上调试口或 UART，在 TEE 初始化后 dump 内存。
7. **交叉验证**：用已知的 op-tee 版本 CVE 对照。

## 四、命令 / 脚本

```bash
# 拆镜像
binwalk -eM firmware.img
unblob firmware.img -o out/        # 更稳的现代替代
# 找签名与公钥
strings -n 8 boot.img | grep -iE 'rsa|sha256|signature|verify|AVB'
# AVB 的签名结构（Android Verified Boot）
avbtool info_image --image vbmeta.img
avbtool verify_image --image boot.img

# OP-TEE 镜像
strings -n 6 tee.bin | grep -iE 'OPTEE|SMC|ta_|uuid'
# ARM Trusted Firmware-A
strings -n 8 bl1.bin | grep -iE 'auth|sign|rotpk'
```

```python
#!/usr/bin/env python3
# 判定"信任根在哪"：扫镜像里的公钥模数与 eFuse 哈希
import re, hashlib, sys

def scan(path):
    d = open(path, 'rb').read()
    sha = hashlib.sha256(d).hexdigest()
    print('文件 SHA256:', sha)
    # RSA 公钥模数常见特征：开头若干字节为大数（modulus 最高位 = 0x80~0xFF）
    for m in re.finditer(rb'(-----BEGIN [A-Z ]*PUBLIC KEY-----)', d):
        print('内嵌 PEM 公钥 @%#x' % m.start())
    for m in re.finditer(rb'\x04\x82\x01\x22\x00', d):        # DER 长度 0x0122 ≈ RSA-2048
        print('疑似 DER RSA-2048 公钥 @%#x' % m.start())
    print('总长度 %d' % len(d))

if __name__ == '__main__':
    scan(sys.argv[1])
```

```bash
#!/usr/bin/env bash
# 降级测试：把旧版固件刷进去，观察是否被 anti-rollback 拒绝
dd if=old_fw.img of=/dev/mtdblock0 bs=1M
# 通过厂商恢复模式（eRecovery / fastboot）
fastboot flash boot old_boot.img
fastboot getvar current-slot
fastboot getvar rollback-index 2>&1 | head
```

```bash
# TrustZone-M 的 NSA/IDAU 配置检查（用 OpenOCD dump 后看寄存器）
openocd -f interface/jlink.cfg -f target/nrf9160.cfg \
  -c "init; halt; mdw 0x50000500 8; mdw 0xE000ED88 1; shutdown"
# 0xE000ED88 = CPACR（浮点/SIMD 权限），0x50000xxx = SPU/IDAU 寄存器
```

## 五、常见坑 / 变体

- **"签名合法但内容恶意"**：签名只保证完整性与来源，不保证安全，降级到有漏洞的合法版本是最常见思路。
- **eFuse 读取被禁 ≠ 密钥不可得**：密钥在启动后会被加载到 SRAM，调试口若未关闭即可 dump。
- **回滚索引（rollback index）**：多数设备会记录版本号并拒绝旧版，先 `avbtool` 看 `rollback_index`。
- **TrustZone-M 的 SAU/IDAU**：安全世界可访问全部内存，攻击面在"安全世界的入参校验"而非边界本身。
- **读保护一次烧写不可逆**：STM32 RDP Level 2、ESP32 的 eFuse secure boot 都是不可逆的，遇到就换思路（毛刺/侧信道）。
- **SMC 接口**：TEE 的每个 SMC 处理函数都是一个 syscall，找 `SMC_FROM_NW` 分支里的 `copy_from_user` 缺失。
- **变体**：Intel Boot Guard（ME 的 OTP）、Nvidia Jetson 的 SBK/KEK、Apple 的 iBoot + Secure Enclave。

## 七、CTF 里最常见的三种出题方式

1. **"签名合法但可降级"**：给两份固件（v1 与 v2），v2 修复了漏洞但 v1 仍可刷入；用 v1 的调试后门拿 shell。
2. **"验签分支可被毛刺跳过"**：结合 `fault-injection-glitch`，目标是让 `memcmp` 的返回值被误判，从而加载未签名镜像。
3. **"TEE 的 SMC 入参越界"**：给一个 OP-TEE 的 TA（Trusted Application），其命令处理函数缺少长度校验，NS 侧构造超长参数即可读 TEE 内存里的密钥。

对应的检查动作：

- 第 1 种：`avbtool info_image --image vbmeta.img` 看 `rollback_index`，再用 `fastboot getvar rollback-index` 确认设备端记录，若版本号未递增即可成功。
- 第 2 种：先用示波器确定验签函数的执行时刻（UART 输出"verifying..."的边沿作触发），再做二维参数扫描。
- 第 3 种：在 TA 的 `TA_InvokeCommandEntryPoint` 里找每个 `case`，确认 `params[].memref.size` 是否被副本长度校验；用 `tee-supplicant` 或自写的 CA 程序构造请求。

**取证侧提示**：安全启动被绕过通常会留下痕迹——eFuse 的 revocation 计数变化、`/proc/cmdline` 里多了 `androidboot.verifiedbootstate=orange`、AVB 变为 `dm-verity` 失效后的 `avb_pvm` 日志。分析时优先读这些状态而非只看镜像。

## 六、参考来源

- [ARM TrustZone 软件架构：安全启动与信任链](https://trustedfirmware-a.readthedocs.io/en/latest/)
- [36C3：TrustZone-M(eh) — 绕过安全启动与 glitch AES](https://www.youtube.com/watch?v=4u6BAH8mEDw)
- [OP-TEE 官方文档（SMC 接口与 TA）](https://optee.readthedocs.io/en/latest/)
- [Android Verified Boot（avbtool 与 vbmeta 签名结构）](https://android.googlesource.com/platform/external/avb/)
- [ARM Trusted Firmware-A 文档（BL1/BL2 验签流程）](https://trustedfirmware-a.readthedocs.io/en/latest/)
