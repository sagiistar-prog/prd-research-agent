"""Self-contained, escaped review artifact. No server, network or stored browser data."""
import html
import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets/review"


def render_review(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    title = html.escape(payload["result"]["summary"]["product_name"])
    template = (ASSETS / "index.html").read_text(encoding="utf-8")
    values = {"TITLE": title, "STYLE": (ASSETS / "style.css").read_text(encoding="utf-8"),
              "SCRIPT": (ASSETS / "review.js").read_text(encoding="utf-8"), "DATA": data}
    return re.sub(r"__(TITLE|STYLE|SCRIPT|DATA)__", lambda match: values[match[1]], template)
