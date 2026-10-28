"""CTF 知识库检索引擎。

模块划分：
    config    配置读取（config.toml）
    parser    Markdown + YAML front-matter 解析、分块、关键词抽取
    fts       SQLite FTS5 关键词检索（含 CJK 二元切分）
    vectors   向量检索（sentence-transformers + sqlite-vec，可降级 numpy）
    fusion    RRF 倒数排序融合
    llm       llama-cpp-python 本地推理（GPU 部分卸载）与 Ollama 后端
    rag       检索增强问答
"""

__version__ = "1.0.0"
