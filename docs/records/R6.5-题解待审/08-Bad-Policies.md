# Bad Policies：从组策略首选项里找到正确字段

DownUnderCTF 2024 · 杂项取证 · [官方赛题与题解目录](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/forensics/badpolicies)。本机用原附件完成解密与回算。

ZIP 展开后是域策略的目录。看见 `Registry.pol` 不用马上读注册表：这道题要的是组策略首选项里的本地账户设置。先在目录中找 `Groups.xml`，再看账户对应的 `Properties` 节点。本题只有一个非空的 `cpassword`。

这个字段是 Base64 包装的密文。缺末尾的 `=` 时补到 4 的倍数再解码。按 [Microsoft 的加密规范](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/2c15cbf0-f086-4c74-8b70-1f2fa45dd4be)使用公开的 32 字节 AES 密钥，初始向量为 16 字节零，用 CBC 模式解密。随后去掉分组填充，按 UTF-16 小端读文字。

本机把解出的字节重新填充并加密，与原密文一致。知识库现有的注册表资料能识别文件类型，但没指到本题所需的 XML 字段。
