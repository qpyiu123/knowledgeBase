"""入库条目的出处、去重和离线算法检查。"""

import importlib
import json
from collections import Counter
from pathlib import Path

import pytest

from kb.library import document_info, read_code
from kb.parser import split_front_matter

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "kb"


@pytest.fixture
def module(monkeypatch):
    monkeypatch.syspath_prepend(str(KB / "_code/r67"))
    return importlib.import_module


def test_curation_and_review_match():
    curation = json.loads(
        (ROOT / "docs/data/r67-curation.json").read_text(encoding="utf-8")
    )
    review = json.loads(
        (ROOT / "docs/data/r67-review.json").read_text(encoding="utf-8")
    )
    assert (
        len(review["items"])
        == len({x["id"] for x in review["items"]})
        == review["records"]
    )
    assert Counter(r["decision"] for r in review["items"]) == review["decisions"]
    accepted = {
        r["id"]: r["refs"][0] for r in review["items"] if r["decision"] == "入库"
    }
    declared = {}
    assert len(curation) == len({r["id"] for r in curation}) == 12
    for row in curation:
        raw = (KB / row["path"]).read_text(encoding="utf-8")
        meta, body = split_front_matter(raw, strict=True)
        assert meta["kind"] == "writeup" and meta["origin_id"] == row["id"]
        assert "## 先看这一步" in body and row["summary"]["text"] in body
        assert set(row["quotes"]) == set(row["quote_sources"])
        sources = {s["id"] for s in row["sources"]}
        assert set(row["checks"]) == sources
        for quote in row["quote_sources"].values():
            assert quote["source_id"] in sources and quote["path"].startswith("题目/")
        for src in row["sources"]:
            assert src["path"] in body
            declared[src["id"]] = row["path"]
        for entry in [
            row["summary"],
            *row["conditions"],
            *row["limits"],
            *row["steps"],
        ]:
            assert entry["evidence"] and set(entry["evidence"]) <= row["quotes"].keys()
        previous = set()
        for step in row["steps"]:
            assert set(step["depends_on"]) <= previous
            previous.add(step["id"])
        info = document_info(KB, row["path"], raw)
        assert [s["path"] for s in info["scripts"]] == row["code"]
        assert all(read_code(KB, c)["summary"] for c in row["code"])
        assert all(asset in body and (KB / asset).is_file() for asset in row["images"])
    assert declared == accepted
    assert len(accepted) == 15
    assert accepted["ctfplus-1978124430441713664"].endswith("/poly-rsa-quotient.md")
    assert (
        next(r for r in review["items"] if r["id"] == "ctfplus-1835674017801965568")[
            "decision"
        ]
        == "同题"
    )


def test_affine_iterations(module):
    fn = module("case_relations")
    assert fn.affine_jump(4, 3, 7, 20, 0) == 4
    for modulus, a, b, start in ((97, 8, 12, 5), (20, 6, 3, 17), (97, 1, 12, 5)):
        x = start
        for _ in range(23):
            x = (a * x + b) % modulus
        assert fn.affine_jump(start, a, b, modulus, 23) == x
        if modulus == 97:
            assert fn.affine_repeat(start, x, a, b, modulus) == fn.affine_jump(
                start, a, b, modulus, 46
            )
    assert fn.affine_repeat(10, 10, 5, -40, 97) == 10
    with pytest.raises(ValueError, match="固定点"):
        fn.affine_repeat(10, 9, 5, -40, 97)


def test_cusp_and_factor_hints(module):
    fn = module("case_relations")
    assert fn.and_xor_pair(13 & 19, 13 ^ 19, 13 * 19) == (13, 19)
    with pytest.raises(ValueError, match="判别式"):
        fn.and_xor_pair(13 & 19, 13 ^ 19, 13 * 19 - 1)
    p = 97
    shift = 5

    def point(t):
        z = pow(t, -1, p)
        return ((shift + z * z) % p, pow(z, 3, p))

    co = (0, -3 * shift, 0, 3 * shift**2, -(shift**3))
    assert fn.cusp_scalar(p, co, point(4), point(28)) == 7
    with pytest.raises(ValueError, match="三重根"):
        fn.cusp_scalar(p, (*co[:-1], 1), point(4), point(28))


def test_field_roots_and_quotient(module):
    pytest.importorskip("sympy")
    fn = module("case_relations")
    p, x, y = 101, 19, 26
    pairs = fn.equation_pairs(p, (13 * y * y + x * y + 5 * x) % p, (7 * y + x * x) % p)
    assert (x, y) in pairs
    assert fn.curve_factor_pairs(7 * 11, 0, (11 - 7**3) % p, p) == [(7, 11)]
    n, e = 13 * 17, 5
    message = [7, 0, 3, 1]
    cipher = fn.cyclic_power(message, e, n)
    assert fn.quotient_message(cipher, e, 13, 17) == message
    with pytest.raises(ValueError, match="重因子"):
        fn.quotient_message(cipher, e, 2, 17)
    with pytest.raises(ValueError, match="非负指数"):
        fn.cyclic_power(message, -1, n)


def test_lift_and_nested_factors(module):
    pytest.importorskip("sympy")
    lift = module("lcg_concat").lift_odd_power
    value = pow(45, 4, 1 << 10)
    assert sorted(lift(value, 4, 10)) == [
        x for x in range(1 << 10) if pow(x, 4, 1 << 10) == value
    ]
    pairs, _ = module("nested_pm1").recover(3 * 5, 19 * 71, bound=32)
    assert set(pairs) == {(3, 19), (5, 71)}


def test_known_nonce_uses_left_digest_bits(module):
    known = module("case_relations").known_nonce_private
    # 7 位群阶，哈希必须取左 7 位。
    r, k, d, n = 7, 11, 23, 101
    digest = b"\xc7\x5a"
    z = int.from_bytes(digest, "big") >> 9
    s = (z + r * d) * pow(k, -1, n) % n
    assert known(r, s, digest, k, n) == d


def test_cbc_from_blocks_and_feedback(module):
    fn = module("case_relations").cbc_from_block_decrypt
    recover = module("padding_transcript").recover
    state, target = bytes(range(16)), b"X" * 16
    plain = b"Fifteen bytes!!"
    assert len(plain) == 15
    padded = plain + b"\x01"
    iv = bytes(a ^ b for a, b in zip(state, padded))
    assert fn(iv + target, bytes(16) + state) == padded
    queries = []
    for length in range(1, 17):
        mixed = bytes(16 - length) + bytes([length]) * length
        probe = bytes(a ^ b for a, b in zip(state, mixed))
        queries.append((probe + target, True))
    queries.append((state + target, False))
    clear, proof = recover(iv + target, queries)
    assert clear == plain and proof["queries_verified"] == 17
    with pytest.raises(ValueError, match="冲突"):
        recover(iv + target, [queries[1], queries[0], *queries[2:]])


def test_snow_spn_and_pixels(module):
    spn = module("nibble_spn")
    cipher = spn.crypt(b"sample blocks!!!", 0x1122335A)
    records, proof = spn.recover(cipher, 0x11223340, 5, b"samp")
    assert records == [(0x1122335A, b"sample blocks!!!")]
    assert proof["all_reencrypted"]
    snow = module("snow_state")
    for kind in (0, 1):
        for word in (0, 1, 0xFFFFFFFF, 0x12345678):
            assert snow.inverse_box(snow.box(word, kind), kind) == word
    px = module("hilbert_pixels")
    restored = px.restore_pixels(bytes(range(48)), 4)
    assert restored[:3] == bytes(range(3))
    assert restored != bytes(range(48))
    with pytest.raises(ValueError, match="RGB"):
        px.restore_pixels(bytes(range(8)), 4)
