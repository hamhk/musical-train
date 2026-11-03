"""Рендер Mermaid -> PNG: локальный mmdc (если есть) либо сервис mermaid.ink."""
import base64
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request

from .errors import DepVizError

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _via_mmdc(text, path):
    exe = shutil.which("mmdc")
    if not exe:
        return False
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "g.mmd")
        with open(src, "w", encoding="utf-8") as f:
            f.write(text)
        r = subprocess.run([exe, "-i", src, "-o", path, "-b", "white"],
                           capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(path)


def _via_mermaid_ink(text, path, timeout=30):
    b64 = base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/{b64}?type=png&bgColor=white"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = r.read()
    except (urllib.error.URLError, TimeoutError) as e:
        raise DepVizError(f"не удалось получить PNG от mermaid.ink: {e}")
    if not data.startswith(PNG_SIG):
        raise DepVizError("mermaid.ink вернул не PNG (возможно, граф слишком большой)")
    with open(path, "wb") as f:
        f.write(data)


def render_png(text, path):
    if _via_mmdc(text, path):
        return
    _via_mermaid_ink(text, path)
