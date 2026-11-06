"""读取知识库中已归档的原图。"""

import re
from pathlib import Path

IMAGE_DIR = "_assets/images"
IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
MAX_IMAGE_BYTES = 16 * 1024 * 1024
IMAGE_NAME = re.compile(r"[0-9a-f]{64}\.(?:png|jpg|gif|webp)")


def image_suffix(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and b"IEND" in data[-16:]:
        return ".png"
    if data.startswith(b"\xff\xd8\xff") and b"\xff\xd9" in data[-64:]:
        return ".jpg"
    if data.startswith((b"GIF89a", b"GIF87a")) and data.endswith(b";"):
        return ".gif"
    if (
        data.startswith(b"RIFF")
        and data[8:12] == b"WEBP"
        and int.from_bytes(data[4:8], "little") + 8 == len(data)
    ):
        return ".webp"
    return None


def read_image(kb_dir: Path, path: str) -> tuple[bytes, str]:
    prefix = IMAGE_DIR + "/"
    if not path.startswith(prefix) or not IMAGE_NAME.fullmatch(path[len(prefix) :]):
        raise ValueError("需要库内配图路径")
    root = kb_dir.resolve()
    file = (root / path).resolve()
    if not file.is_relative_to(root / IMAGE_DIR):
        raise ValueError("配图路径越界")
    with file.open("rb") as stream:
        data = stream.read(MAX_IMAGE_BYTES + 1)
    suffix = image_suffix(data)
    if len(data) > MAX_IMAGE_BYTES or suffix != file.suffix:
        raise ValueError("配图过大或格式不符")
    return data, IMAGE_MIME[suffix]
