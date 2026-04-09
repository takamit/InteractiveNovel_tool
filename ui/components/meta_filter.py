from __future__ import annotations

import re

_META_PATTERNS = [
    r"今回の",
    r"主な更新",
    r"確認した範囲",
    r"正確に言うと",
    r"次は",
    r"段階",
    r"版$",
    r"製品",
    r"自然なのは",
]


def remove_meta_lines(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append(raw_line)
            continue
        if any(re.search(pattern, line) for pattern in _META_PATTERNS):
            continue
        lines.append(raw_line)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)
