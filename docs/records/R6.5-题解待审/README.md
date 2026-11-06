# 题解待审：本机回验和站点结果

日期：2026-11-06。来源是前三轮的原附件。本目录供审核，不属于正式知识库，未更改原文、导入配置或索引。题解用自己的话说明为什么做这一步，并保留出处。赛题答案、登录信息和原附件不进 Git。

## 已完成

| 范围 | 题解 | 怎样核对 |
| --- | --- | --- |
| 站点 2 题 | [you_raise_me_up](01-you_raise_me_up.md)、[FireFox Forensics](02-FireFox-Forensics.md) | 从原附件分别还原，DASCTF 两题均显示回答正确。之后按新要求停止站点操作。 |
| 用户本地密码库 10 题 | [PolyRSA](03-PolyRSA.md)、[消逝的曲线](04-消逝的曲线.md)、[Factorize](05-Factorize.md)、[Lunar LCG](06-Lunar-LCG.md)、[NTRU](07-NTRU.md)、[highlow](15-highlow.md)、[Algebra](16-Algebra.md)、[lwe1](17-lwe1.md)、[ez_raabin](18-ez_raabin.md)、[Subgroup Choreographer](19-Subgroup-Choreographer.md) | 用公开密文、曲线点、状态序列或生成公式逐题回验。Factorize 另有公开重托管版，本轮验证的是本地原附件。 |
| 赛事原件离线 6 题 | [Bad Policies](08-Bad-Policies.md)、[Wacky Recipe](09-Wacky-Recipe.md)、[USB Hacker](10-USB-Hacker.md)、[Beep Boop Robot](11-Beep-Boop-Robot.md)、[Miniscule](12-Miniscule.md)、[Nothing to See](13-Nothing-to-See.md) | 用本地原附件回验，未到站点提交。Nothing to See 从 PNG 的标题字段取得 ZIP 密码，解出的文件校验通过。 |
| 逆向资料 1 篇 | [jocker 公开题解导读](14-jocker-公开题解导读.md) | 核对题名与赛事，只做原文导读。UTCTF 搜到的 2019 同名题、以及同名 ezVM 的其他赛事文章，未当作本题题解。 |

## 暂存进度

- 站点题中其余样本跳过后续提交。Nuclear wastewater 已核对公开题解的像素频率线索和内层 ZIP 校验，未记为解完；菜刀流量已从题目抓包识别出文件传输，未提交。Teslaaaaa 的公开资料涉及固件逆向，本轮不再试解。
- 第三轮其余赛事附件保留原状：ZFS 文件恢复、打不开的盒、TAS概论大作业、熙熙攘攘我们的天才吧、新穷铁道、emuc2、Macro Magic、Sam I Am、DNA Decay、doxme、Rage!、Land Down Under、Tornado Warning、Spam 2023。先前记录里的静态证据仍可用；这些题未列入本次完成数。
- 本机试算代码保留在 `work/r65-writeups/`，前两轮已有的验证脚本仍在 `work/r65-round2/`、`work/r65-misc/`。试算脚本读附件数据，不运行赛题程序。
- [旧文档审查](旧文档审查.md)有 8 项建议。优先审查 PNG、ZIP、音频和 LCG 四篇；批准后再改正式文章和索引。

## 审阅包检查

Python 自动测试 494 通过、1 跳过。待审目录的 21 份 Markdown 文件已核对链接和格式。全文、向量、关系索引及其清单的文件校验值与审查前一致。
