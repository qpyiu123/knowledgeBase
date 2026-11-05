"""统一配置字段与本机个人设置；仓库默认值不随界面保存改写。"""
from __future__ import annotations

import json
import math
from pathlib import Path
from tempfile import NamedTemporaryFile

# section.key: (分组, 名称, 默认值, 可选值/范围, 生效时间)
FIELDS = {
    "ui.theme": ("外观与使用", "主题", "auto", ("auto", "light", "dark"), "立即"),
    "ui.translation": ("外观与使用", "默认翻译方向", "zh", ("zh", "en"), "立即"),
    "search.top_k": ("搜索与索引", "结果数量", 8, (1, 50), "立即"),
    "ui.semantic": ("搜索与索引", "默认补充语义结果", False, (), "立即"),
    "ui.conditions": ("搜索与索引", "默认显示条件关联", False, (), "立即"),
    "ui.generation": ("模型", "启动方式", "on_demand", ("on_demand", "manual", "off"), "立即"),
    "llama_server.model": ("模型", "本地模型", "qwen35-9b", ("qwen35-9b", "qwen35-4b"), "下次启动模型"),
    "llama_server.compute": ("模型", "运行方式", "vulkan", ("vulkan", "cpu"), "下次启动模型"),
    "llama_server.device": ("模型", "Vulkan 设备", "auto", (), "下次启动模型"),
    "llm.n_threads": ("模型", "CPU 线程", 6, (1, 64), "下次启动模型"),
    "llm.n_ctx": ("模型", "上下文长度", 8192, (512, 32768), "下次启动模型"),
    "llm.n_gpu_layers": ("模型", "显卡层数", 99, (0, 999), "下次启动模型"),
    "llm.max_tokens": ("模型", "最大输出长度", 1200, (1, 8192), "下次启动模型"),
    "llm.temperature": ("模型", "输出随机程度", 0.2, (0, 2), "下次启动模型"),
    "llm.timeout": ("模型", "请求超时（秒）", 300, (10, 900), "下次启动模型"),
    "kb.kb_dir": ("资料与工作区", "资料目录", "kb", (), "重启应用"),
    "workspace.dir": ("资料与工作区", "工作区目录", "work/workspaces", (), "重启应用"),
    "attachment.dir": ("资料与工作区", "附件目录", "work/attachments", (), "重启应用"),
    "attachment.max_bytes": ("资料与工作区", "附件上限（字节）", 8388608, (1024, 67108864), "立即"),
    "feedback.file": ("资料与工作区", "反馈文件", "work/feedback/feedback.jsonl", (), "重启应用"),
    "runtime.python": ("高级", "Python 解释器", "auto", (), "重启应用"),
    "runtime.port": ("高级", "网页端口", 8765, (1024, 65535), "重启应用"),
    "llama_server.port": ("高级", "推理端口", 8766, (1024, 65535), "下次启动模型"),
    "kb.index_dir": ("高级", "索引目录", "index", (), "重启应用"),
    "search.rrf_k": ("高级", "结果合并参数", 60, (1, 200), "重启应用"),
    "search.chunk_chars": ("高级", "资料片段长度", 900, (128, 8192), "更新索引后重启"),
    "search.chunk_overlap": ("高级", "片段重叠长度", 120, (0, 2048), "更新索引后重启"),
    "embed.batch_size": ("高级", "编码批量大小", 32, (1, 128), "重启应用"),
}
OVERRIDES = {
    "runtime.python": "KB_PYTHON", "runtime.port": "AGENT_PORT",
    "llama_server.model": "KB_CHAT_MODEL", "llama_server.port": "KB_MODEL_PORT",
    "llm.n_gpu_layers": "KB_N_GPU_LAYERS", "llama_server.compute": "KB_CPU_ONLY",
    "workspace.dir": "AGENT_WORKSPACE_DIR", "attachment.dir": "AGENT_ATTACHMENT_DIR",
    "attachment.max_bytes": "AGENT_ATTACHMENT_MAX_BYTES", "feedback.file": "AGENT_FEEDBACK_FILE",
}


def location(config_path: Path) -> Path:
    return config_path.parent / "work/settings.json"


def normalize(changes) -> dict:
    if not isinstance(changes, dict):
        raise ValueError("设置必须是字段表")
    result = {}
    for key, value in changes.items():
        if key not in FIELDS:
            raise ValueError(f"无法修改设置：{key}")
        _, label, default, limits, _ = FIELDS[key]
        if type(default) is float:
            valid = type(value) in (int, float) and math.isfinite(value)
        else:
            valid = type(value) is type(default)
        if valid and limits:
            valid = limits[0] <= value <= limits[1] if isinstance(default, (int, float)) else value in limits
        if valid and isinstance(value, str):
            valid = bool(value.strip()) and len(value) <= 500 and not any(c in value for c in "\r\n\0")
        if not valid:
            raise ValueError(f"请检查「{label}」的值")
        result[key] = value
    return result


def read(config_path: Path) -> dict:
    path = location(config_path)
    return normalize(json.loads(path.read_text(encoding="utf-8-sig"))) if path.exists() else {}


def save(config_path: Path, values: dict) -> None:
    path = location(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as temp:
        json.dump(normalize(values), temp, ensure_ascii=False, indent=2)
        temp.write("\n")
        staged = Path(temp.name)
    try:
        staged.replace(path)
    finally:
        staged.unlink(missing_ok=True)
