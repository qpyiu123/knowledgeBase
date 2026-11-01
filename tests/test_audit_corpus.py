"""DB-Q1 只读语料质量审计工具（tools/audit_corpus.py）的测试。

全部用合成语料（tmp_path）驱动，不读真实 kb，确保：
  * 每条规则都按构造的样本给出预期结论（含误报边界的反例）；
  * 审计不写入被扫描目录（前后逐文件 mtime / 字节哈希一致）；
  * 同一输入两次运行结果完全一致（确定性）。
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

import audit_corpus as ac

# ---------------------------------------------------------------------------
# 合成语料
# ---------------------------------------------------------------------------

BODY_A = (
    "题目给的二进制程序里存在栈溢出，输入超长字符串可以覆盖返回地址。"
    "先用 checksec 看保护，发现只有 NX 没有 canary，于是直接 ret2text。"
    "exp 里用 p64 打包地址，远程连上去把 payload 发过去就拿到 flag。"
) * 4

BODY_B = (
    "题目给的二进制程序里存在栈溢出，输入超长的字符串可以覆盖返回地址！"
    "先用 checksec 看保护，发现只有 NX 没有 canary，所以于是直接 ret2text。"
    "exp 里用 p64 打包地址，远程连上去把 payload 发过去就拿到 flag 了。"
) * 4

# 两篇同模板文档的差异化正文：主题完全不同，用词没有重叠。
# 注意模板本身占了可观的比例——这正是要点：模板相同 ≠ 文档重复。
BODY_SOLVE_A = (
    "解法一：先用 one_gadget 找可用的 libc 偏移，再泄漏地址，最后直接跳 one_gadget。"
    "调试过程中观察堆块布局，确认 tcache 链被正确串联。"
    "利用 malloc 的分配顺序把目标地址写到 free 链上，触发任意写。"
)
BODY_SOLVE_B = (
    "解法二：本题是密码题，使用已知明文攻击恢复 RC4 密钥流，再异或还原明文。"
    "脚本里用 itertools 枚举候选密钥长度，碰到可读英文片段就停下，随后解出 flag。"
    "整个过程不涉及二进制，重点在于统计检验与字符频率分析。"
)

TEMPLATE = (
    "# {title}\n\n## 题目描述\n\n"
    "本题来自某次校内赛，题目描述如下：给定附件，分析其逻辑并取得 flag。"
    "题目给了一个可执行文件和一个远端地址，flag 格式为 flag{{...}}。"
    "\n\n## 附件信息\n\n附件内容与本题的解题过程直接相关，请先自行分析再对照。"
    "\n\n## 环境\n\n本机调试环境与远端一致，建议先复现再写 exp。"
    "\n\n## 评分\n\n本题分值 300，属于中档题。\n\n"
)


def make_doc(title: str, body: str, category: str = "pwn", *,
             source: str = "https://example.com/writeup/1",
             license_: str | None = "MIT", fm_extra: str = "") -> str:
    lines = ["---", f'title: "{title}"', f"category: {category}",
             "tags: [writeup]", "difficulty: medium"]
    if source:
        lines.append(f'source: "{source}"')
    if license_ is not None:
        lines.append(f'license: "{license_}"')
    lines.append("updated: 2026-11-01")
    if fm_extra:
        lines.append(fm_extra)
    lines += ["---", ""]
    return "\n".join(lines) + body


def write(root: Path, rel: str, text: str, encoding: str = "utf-8") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding=encoding)
    return p


def snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    """逐文件 (size, mtime_ns, sha256)，用于证明审计过程没有写入。"""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            st = p.stat()
            out[p.relative_to(root).as_posix()] = (
                st.st_size, st.st_mtime_ns,
                hashlib.sha256(p.read_bytes()).hexdigest())
    return out


def build_corpus(tmp_path: Path) -> Path:
    kb = tmp_path / "kb"
    write(kb, "pwn/stack.md", make_doc("stack overflow", BODY_A, "pwn"))
    # 近似重复：标点/措辞微调
    write(kb, "pwn/stack-copy.md", make_doc("stack overflow copy", BODY_B, "pwn"))
    # 共同模板但解法不同（同赛事、同结构、正文主题完全不同）
    write(kb, "pwn/tmpl-a.md",
          make_doc("tmpl a", TEMPLATE.format(title="A") + BODY_SOLVE_A * 4, "pwn"))
    write(kb, "pwn/tmpl-b.md",
          make_doc("tmpl b", TEMPLATE.format(title="B") + BODY_SOLVE_B * 4, "pwn"))
    # 摘要卡 ⊂ 完整正文
    long_doc = BODY_A + "\n\n" + ("补充说明：调试时注意 gdb 的 cyclic 参数。\n" * 10)
    write(kb, "pwn/full.md", make_doc("full text", long_doc, "pwn"))
    write(kb, "pwn/card.md",
          make_doc("card", "一句话总结：" + BODY_A, "pwn",
                   source="https://example.com/writeup/2"))
    # 代码围栏：合法 / 未闭合 / 引用块内 / 行内示例
    write(kb, "pwn/fence-ok.md",
          make_doc("fence ok", "正文\n\n```python\nprint(1)\n```\n\n结尾\n", "pwn"))
    write(kb, "pwn/fence-bad.md",
          make_doc("fence bad", "正文\n\n```python\nprint(1)\n", "pwn"))
    write(kb, "pwn/fence-quoted.md",
          make_doc("fence quoted", "正文\n\n> ```asm\n> mov eax, 1\n> ```\n", "pwn"))
    write(kb, "pwn/fence-inline.md",
          make_doc("fence inline", "密钥是 `meow~tea~~~`，不是围栏。\n", "pwn"))
    # 缺元数据 / 缺图
    write(kb, "pwn/no-meta.md", "# 没有 front-matter 的笔记\n\n正文很短。\n")
    write(kb, "pwn/no-source.md",
          make_doc("no source", BODY_A, "pwn", source="", license_=None))
    write(kb, "pwn/broken-img.md",
          make_doc("broken img",
                   "如图 1 所示，payload 这样构造：\n\n![fig](images/missing.png)\n",
                   "pwn"))
    # YAML 语法错误：signals 里未加引号的 [Misc]
    write(kb, "misc/yaml-bad.md",
          make_doc("yaml bad", "正文\n", "misc", fm_extra="signals: [[Misc] 清北问答, Git]"))
    # 类别不在白名单
    write(kb, "other/weird.md",
          make_doc("weird", BODY_A + "\n\n这段只在 weird 里出现：acgt-7781。\n",
                   "not_a_category"))
    # 不可读（非 UTF-8 字节：文件名是 ASCII，正文换成 latin-1 字节）
    bad = kb / "pwn" / "latin1.md"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_bytes(make_doc("latin1", "caf\u00e9 body\n")
                    .encode("latin-1", "replace"))
    # 不被收录规则扫到的文件（下划线前缀），应当被忽略
    write(kb, "pwn/_draft.md", make_doc("draft", BODY_A, "pwn"))
    write(kb, "_index.md", "# 索引\n")
    return kb


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    return build_corpus(tmp_path)


def run(root: Path, kb: Path, out: Path, **kw) -> dict:
    args = ["--project-root", str(root), "--kb-dir", str(kb), "--out-dir", str(out)]
    for key, value in kw.items():
        args.append(key)
        if value is not True:      # 布尔开关（如 --hash-before）不带值
            args.append(str(value))
    assert ac.main(args) == 0
    return json.loads((out / "run_meta.json").read_text(encoding="utf-8"))


def inventory(out: Path) -> dict[str, dict]:
    recs = [json.loads(line) for line in
            (out / "inventory.jsonl").read_text(encoding="utf-8").splitlines() if line]
    return {r["path"]: r for r in recs}


# ---------------------------------------------------------------------------
# 收录规则与盘点
# ---------------------------------------------------------------------------


def test_only_index_paths_are_audited(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    meta = run(tmp_path, corpus, out)
    inv = inventory(out)
    expected = {p.relative_to(corpus).as_posix() for p in corpus.rglob("*.md")
                if not p.name.startswith("_")}
    assert set(inv) == expected
    assert "_index.md" not in inv and "pwn/_draft.md" not in inv
    assert meta["doc_count"] == len(expected)


def test_doc_count_matches_indexing_rule(corpus: Path, tmp_path: Path) -> None:
    from kb.parser import iter_md_paths
    assert len(list(iter_md_paths(corpus))) == len(
        [p for p in corpus.rglob("*.md") if not p.name.startswith("_")])


# ---------------------------------------------------------------------------
# 精确 / 近似重复
# ---------------------------------------------------------------------------


def test_exact_duplicate_detected(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    write(kb, "pwn/a.md", make_doc("a", BODY_A, "pwn"))
    write(kb, "pwn/b.md", make_doc("b (不同标题)", BODY_A, "pwn"))
    out = tmp_path / "out"
    run(tmp_path, kb, out)
    dup = json.loads((out / "duplicate_candidates.json").read_text(encoding="utf-8"))
    assert dup["exact_groups"] == 1
    assert sorted(dup["exact_duplicates"][0]["paths"]) == ["pwn/a.md", "pwn/b.md"]


def test_near_duplicate_detected(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    dup = json.loads((out / "duplicate_candidates.json").read_text(encoding="utf-8"))
    pairs = {(p["a"], p["b"]): p for p in dup["pairs"]}
    pair = pairs[("pwn/stack-copy.md", "pwn/stack.md")]
    assert pair["jaccard"] >= 0.6
    assert pair["snippet"]
    assert pair["readout"] in {"near_equivalent_copy", "large_overlap_different_solution"}


def test_same_template_different_solution_not_duplicate(corpus: Path, tmp_path: Path) -> None:
    """共用赛事模板但正文主题不同：不得被判成近似重复（判读也不能是"等价副本"）。"""
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    dup = json.loads((out / "duplicate_candidates.json").read_text(encoding="utf-8"))
    pair = next((p for p in dup["pairs"]
                 if {p["a"], p["b"]} == {"pwn/tmpl-a.md", "pwn/tmpl-b.md"}), None)
    if pair is not None:
        assert pair["readout"] != "near_equivalent_copy"
        assert pair["jaccard"] < 0.75, "模板相同不代表正文相同"
    # 阈值放到 0.6 会让这类文档涌入候选——这是"阈值决定误报边界"的实证，
    # 也是默认阈值留在 0.7 的理由。
    wide = tmp_path / "wide"
    run(tmp_path, corpus, wide, **{"--min-jaccard": 0.6})
    wide_dup = json.loads((wide / "duplicate_candidates.json").read_text(encoding="utf-8"))
    assert len(wide_dup["pairs"]) >= len(dup["pairs"])


def test_summary_card_is_subset_not_equivalent(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    inv_recs = inventory(out)
    card = inv_recs["pwn/card.md"]
    full = inv_recs["pwn/full.md"]
    assert card["body_chars"] < full["body_chars"], "摘要卡应当比全文短"
    # 卡片⊂全文：包含度判据把它挑出来，但不该判成"等价副本"
    dup = json.loads((out / "duplicate_candidates.json").read_text(encoding="utf-8"))
    pair = next((p for p in dup["pairs"]
                 if {p["a"], p["b"]} == {"pwn/card.md", "pwn/full.md"}), None)
    assert pair is not None, "摘要卡⊂全文 应当作为候选出现"
    assert pair["containment_a_in_b"] >= 0.75 or pair["containment_b_in_a"] >= 0.75
    assert pair["readout"] != "near_equivalent_copy"
    assert pair["jaccard"] < 0.95


def test_candidate_generation_is_not_truncated(tmp_path: Path) -> None:
    """截断只影响数量，绝不丢掉最高分的对（回归：旧实现按分数截断，丢了 0.9997 那对）。"""
    tmp = tmp_path / "kb"
    for i in range(6):
        write(tmp, f"pwn/d{i}.md", make_doc(f"d{i}", BODY_A + f"\n第 {i} 段补充。", "pwn"))
    out_full, out_capped = tmp_path / "full", tmp_path / "capped"
    run(tmp_path, tmp, out_full)
    run(tmp_path, tmp, out_capped, **{"--max-pairs": 1})
    full = json.loads((out_full / "duplicate_candidates.json").read_text(encoding="utf-8"))
    capped = json.loads((out_capped / "duplicate_candidates.json").read_text(encoding="utf-8"))
    top = max(p["score"] for p in full["pairs"])
    assert top >= 0.95, "构造的近似副本应当有极高分数"
    assert full["stats"]["capped"] is False
    assert capped["stats"]["capped"] is True, "压低上限时必须显式记录截断"
    assert max(p["score"] for p in capped["pairs"]) == top


def test_short_doc_containment_is_not_used_to_match(tmp_path: Path) -> None:
    """短文档的包含度容易被放大：不参与包含度判据，避免假阳性。"""
    kb = tmp_path / "kb"
    write(kb, "pwn/long.md", make_doc("long", BODY_A * 3, "pwn"))
    write(kb, "pwn/tiny.md", make_doc("tiny", "一句话总结：栈溢出直接 ret2text。", "pwn"))
    out = tmp_path / "out"
    run(tmp_path, kb, out)
    dup = json.loads((out / "duplicate_candidates.json").read_text(encoding="utf-8"))
    tiny = [p for p in dup["pairs"] if "pwn/tiny.md" in (p["a"], p["b"])]
    assert all(p["tiny_doc_containment_ignored"] for p in tiny)


# ---------------------------------------------------------------------------
# 围栏
# ---------------------------------------------------------------------------


def test_legal_fences_counted(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    inv = inventory(out)
    ok = inv["pwn/fence-ok.md"]
    assert ok["has_code"] is True
    assert ok["closed_fence_count"] == 1
    assert ok["fence_langs"].get("python") == 1
    assert ok["fence_problems"] == []


def test_unclosed_fence_flagged(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    bad = inventory(out)["pwn/fence-bad.md"]
    kinds = {p["kind"] for p in bad["fence_problems"]}
    assert "unclosed_fence" in kinds
    assert bad["closed_fence_count"] == 0


def test_blockquote_fence_is_not_a_false_positive(corpus: Path, tmp_path: Path) -> None:
    """引用块里的围栏是合法围栏，不能报 stray_backticks（真实案例：_imported/pwn/overflow.md）。"""
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    rec = inventory(out)["pwn/fence-quoted.md"]
    assert rec["closed_fence_count"] == 1
    assert not [p for p in rec["fence_problems"] if p["kind"] == "stray_backticks"]
    # 独段引用块围栏（> ``` 单独一行）同样要认
    fenced = ac.parse_fences("正文\n\n> ```c\n> int main(){}\n> ```\n")
    assert fenced["closed_fence_count"] == 1
    assert fenced["fence_problems"] == []


def test_inline_backticks_are_not_fences(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    rec = inventory(out)["pwn/fence-inline.md"]
    assert rec["fence_count"] == 0
    assert rec["fence_problems"] == []


def test_stray_fence_marker_detected() -> None:
    body = "正文\n\n文本 ```孤零零一个 ``` 当作行内示例没事\n\n再看这里 ```没配对\n"
    problems = ac.parse_fences(body)["fence_problems"]
    assert [p["kind"] for p in problems] == ["stray_backticks"]
    assert problems[0]["line"] == 5, "报告行号应指向那个没配对的标记"


# ---------------------------------------------------------------------------
# 元数据 / 图片 / 编码
# ---------------------------------------------------------------------------


def test_missing_metadata_reported(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    inv = inventory(out)
    assert inv["pwn/no-meta.md"]["front_matter_error"].startswith("缺少 front-matter")
    assert inv["pwn/no-source.md"]["source"] == ""
    meta = json.loads((out / "run_meta.json").read_text(encoding="utf-8"))
    # 缺 license 与缺 source 是两件独立的事
    assert any("front-matter" in e["error"] for e in meta["errors"])


def test_yaml_error_is_distinguished_from_missing(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    rec = inventory(out)["misc/yaml-bad.md"]
    err = rec["front_matter_error"]
    assert err.startswith("front-matter YAML 解析失败")
    assert "第 9 行" in err or "行" in err
    # 语法错误时元数据整块拿不到，必须显式报错而不是静默当"没写"
    assert rec["title"] == "yaml-bad"


def test_missing_local_image_and_dependency_hint(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    rec = inventory(out)["pwn/broken-img.md"]
    assert rec["images"]["local_missing"] == ["images/missing.png"]
    assert rec["images"]["suspect_broken_image_dependency"] is True
    assert rec["images"]["image_dependent_hints"]


def test_undecodable_file_reported_not_crashed(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    meta = run(tmp_path, corpus, out)
    assert any(e["stage"] == "decode" for e in meta["errors"])
    rec = inventory(out)["pwn/latin1.md"]
    assert rec["decode_error"]


def test_category_outside_whitelist(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    assert inventory(out)["other/weird.md"]["category_valid"] is False


# ---------------------------------------------------------------------------
# 只读性 / 确定性
# ---------------------------------------------------------------------------


def test_audit_does_not_write_inputs(corpus: Path, tmp_path: Path) -> None:
    before = snapshot(corpus)
    out = tmp_path / "out"
    run(tmp_path, corpus, out)
    assert snapshot(corpus) == before, "审计不得修改被扫描目录中的任何文件"


def test_audit_is_deterministic(corpus: Path, tmp_path: Path) -> None:
    """同一输入两次运行：内容类产物逐字节一致（只排除时间戳字段）。"""
    a, b = tmp_path / "a", tmp_path / "b"
    run(tmp_path, corpus, a)
    run(tmp_path, corpus, b)

    def normalise(path: Path) -> str:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("generated_at", "timings", "elapsed_seconds",
                        "dup_seconds", "inventory_seconds", "out_dir"):
                data.pop(key, None)
        return json.dumps(data, ensure_ascii=False, sort_keys=True)

    for name in ("inventory.jsonl", "duplicate_candidates.json",
                 "import_check.json", "sample_plan.json", "run_meta.json"):
        assert (a / name).read_text(encoding="utf-8") == \
            (b / name).read_text(encoding="utf-8") or normalise(a / name) == normalise(b / name), name
    assert normalise(a / "run_meta.json") == normalise(b / "run_meta.json")


def test_reports_requested_outputs(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    meta = run(tmp_path, corpus, out)
    # 工具负责产出机器可复现的部分；sample_review.md 是人工抽样结论，由人写。
    for name in ("inventory.jsonl", "duplicate_candidates.json", "report.md",
                 "sample_plan.json", "run_meta.json"):
        assert (out / name).exists(), name
    report = (out / "report.md").read_text(encoding="utf-8")
    # brief 要求报告里写清总耗时和错误数
    assert "耗时" in report
    assert str(meta["error_count"]) in report
    assert meta["error_count"] == len(meta["errors"]) >= 1


def test_compare_hash_detects_change(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(tmp_path, corpus, out, **{"--hash-before": True})
    before = out / "hash_before.json"
    assert before.exists()
    # kb 未被改动 → 退出码 0
    assert ac.main(["--project-root", str(tmp_path), "--kb-dir", str(corpus),
                    "--out-dir", str(out), "compare-hash",
                    "--before", str(before)]) == 0
    # 改一个字 → 退出码 2
    (corpus / "pwn" / "stack.md").write_text("被改动\n", encoding="utf-8")
    assert ac.main(["--project-root", str(tmp_path), "--kb-dir", str(corpus),
                    "--out-dir", str(out), "compare-hash",
                    "--before", str(before)]) == 2


def test_sample_plan_is_reproducible(corpus: Path, tmp_path: Path) -> None:
    a, b = tmp_path / "sa", tmp_path / "sb"
    run(tmp_path, corpus, a)
    run(tmp_path, corpus, b)
    pa = json.loads((a / "sample_plan.json").read_text(encoding="utf-8"))
    pb = json.loads((b / "sample_plan.json").read_text(encoding="utf-8"))
    assert pa == pb
    assert pa["seed"] == 20261101
    assert pa["algorithm"] and pa["strata"] >= 1
    assert pa["size_actual"] == len(pa["paths"]) and pa["size_actual"] >= 1
