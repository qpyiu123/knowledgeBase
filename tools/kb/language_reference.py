"""从已有 Markdown 卡片的小节建立函数入口，保存在同一 FTS 数据库。"""
from __future__ import annotations

import re
import sqlite3

from .parser import split_sections

TABLE = """
CREATE TABLE IF NOT EXISTS api_sections (
    path TEXT, category TEXT, heading TEXT, symbol TEXT, language TEXT,
    version TEXT, source TEXT, explanation TEXT, PRIMARY KEY(path, heading, symbol)
);
"""
ALIASES = {
    "Python": ("python", "py"),
    "PHP": ("php",),
    "Node.js": ("node.js", "nodejs", "node"),
    "JavaScript": ("javascript", "js"),
    "C": ("c",),
    "C++": ("c++", "cpp"),
    "Go": ("golang", "go"),
    "Java": ("java",),
}
IDENTIFIER = r"[A-Za-z_][A-Za-z_0-9]*(?:(?:\.|::)[A-Za-z_][A-Za-z_0-9]*)*"


def index_rows(doc):
    if not doc.api_symbols and doc.kind != "api":
        return []
    language = doc.api_language or next((x for x in doc.tags if x in ALIASES), "")
    if not language:
        return []
    explicit = {x.casefold(): x for x in doc.api_symbols}
    out = []
    for heading, text in split_sections(doc.body):
        head = heading.strip("` ")
        match = re.match(rf"^(?:class )?({IDENTIFIER})(?=\s*(?:\(|$))", head)
        if not match:
            continue
        symbol = match[1]
        if explicit and symbol.casefold() not in explicit:
            continue
        if not explicit and "(" not in head:
            continue
        url = re.search(r"(?m)^来源：.*?\((https://[^)\s]+)\)", text)
        source = url[1] if url else (doc.source + "#" + symbol
                                     if language == "Python" and doc.source.startswith("https://docs.python.org/")
                                     else doc.source)
        explanation, fenced = "", False
        for line in text.splitlines():
            if line.lstrip().startswith("```"):
                fenced = not fenced
            elif not fenced and re.search(r"[\u4e00-\u9fa5]", line) and not line.startswith(("来源：", ">", "    ")):
                explanation = line.strip()
                break
        if not explanation:
            continue
        out.append((doc.path, doc.category, heading, symbol, language, doc.api_version, source, explanation[:500]))
    return out


def _contains(text, symbol):
    return re.search(r"(?<![A-Za-z0-9_:.])" + re.escape(symbol) + r"(?![A-Za-z0-9_:.])",
                     text, flags=re.IGNORECASE) is not None


def language_prefix(query):
    for label, names in ALIASES.items():
        for name in names:
            found = re.match(re.escape(name) + r"(?=\s|[:：]|$)", query, re.IGNORECASE)
            if found:
                return label, query[found.end():].lstrip(" :：")
    return "", query


def lookup(connection, query, limit, scoped=False):
    language, rest = language_prefix(query.strip())
    # 普通搜索只接管明确的“语言 + 函数”短查询；完整题面继续走原检索。
    if not scoped and (not language or not re.fullmatch(IDENTIFIER + r"(?:\([^)]*\))?", rest)):
        return []
    try:
        rows = connection.execute("SELECT * FROM api_sections ORDER BY path, symbol").fetchall()
    except sqlite3.OperationalError as error:
        if "no such table" not in str(error):
            raise
        return []
    matches = []
    for path, category, heading, symbol, lang, version, source, explanation in rows:
        if language and language != lang:
            continue
        short = re.split(r"\.|::", symbol)[-1]
        score = 3 if _contains(rest, symbol) else 2 if _contains(rest, short) else 0
        if scoped and language and not rest:
            score = 1
        if scoped and not score and not re.search(r"[A-Za-z0-9_]", rest):
            words = re.findall(r"[一-龥]+", rest)
            pairs = {word[i:i+2] for word in words for i in range(len(word)-1)}
            hits = sum(pair in explanation for pair in pairs)
            if hits >= 2:
                score = min(hits, 9) / 10
        if not score:
            continue
        # Reader 与这里采用同一套标题锚点规则。
        anchor = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fa5]+", "-", heading.lower().replace("`", "")).strip("-")[:60] or "sec"
        item = {"path": path, "category": category, "title": f"{lang} · {symbol}", "section": heading,
                "score": float(score), "snippet": explanation, "doc_type": "topic",
                "doc_type_label": "语言文档", "api": {"symbol": symbol, "language": lang,
                "version": version, "source": source, "anchor": anchor}}
        matches.append((score, item))
    matches.sort(key=lambda row: -row[0])
    return [item for _, item in matches[:limit]]
