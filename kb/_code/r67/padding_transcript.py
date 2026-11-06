"""重放赛题抓包已经记录的 CBC 填充反馈。只使用已有请求和响应，不发送请求。"""

# 取自《密码学题解汇编》shared/src/cryptoexp/utils/padding_transcript.py。
# 原作者 coolmoon & guaidao2，MIT 许可见同目录 LICENSE.txt。


def valid_padding(raw):
    return (
        bool(raw)
        and 1 <= raw[-1] <= 16
        and raw[-raw[-1] :] == bytes([raw[-1]]) * raw[-1]
    )


def recover(original, queries, check=lambda: None):
    if (
        type(original) is not bytes
        or not 32 <= len(original) <= 8192
        or len(original) % 16
    ):
        raise ValueError("原文封装须为 IV 加完整 CBC 分组")
    if type(queries) is not list or not 16 <= len(queries) <= 100000:
        raise ValueError("离线反馈数量越界")
    targets = {original[i : i + 16] for i in range(16, len(original), 16)}
    success = {t: [] for t in targets}
    for q, accepted in queries:
        check()
        if type(q) is not bytes or len(q) != 32 or type(accepted) is not bool:
            raise ValueError("反馈须为明确的 32 字节 IV/分组和布尔值")
        if q[16:] not in targets:
            raise ValueError("存在不属于原密文的目标分组，未混用会话")
        if accepted:
            success[q[16:]].append(q[:16])
    intermediate = {}
    for target, ivs in success.items():
        if len(ivs) != 16:
            raise ValueError(
                "每个目标必须有按 padding=1..16 顺序的 16 次成功反馈；未猜缺失字节"
            )
        state = bytearray(16)
        for pad, iv in enumerate(ivs, 1):
            state[-pad] = iv[-pad] ^ pad
        intermediate[target] = bytes(state)
    for q, accepted in queries:
        check()
        raw = bytes(a ^ b for a, b in zip(q[:16], intermediate[q[16:]]))
        if valid_padding(raw) != accepted:
            raise ValueError("恢复值与原始成功/失败反馈冲突；可能有假阳性、重排或缺包")
    padded = b"".join(
        bytes(
            a ^ b
            for a, b in zip(original[i - 16 : i], intermediate[original[i : i + 16]])
        )
        for i in range(16, len(original), 16)
    )
    if not valid_padding(padded):
        raise ValueError("完整恢复消息未通过 PKCS#7 填充校验")
    return padded[: -padded[-1]], {
        "blocks": len(original) // 16 - 1,
        "queries_verified": len(queries),
        "successes_verified": sum(ok for _, ok in queries),
        "all_feedback_verified": True,
        "padding_verified": True,
        "key_recovered": False,
        "authentication_claimed": False,
    }
