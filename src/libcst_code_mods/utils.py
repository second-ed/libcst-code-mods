from __future__ import annotations

import black


def black_format(code: str, line_length: int = 120, *, magic_trailing_comma: bool = False) -> str:
    return black.format_str(
        code, mode=black.FileMode(line_length=line_length, magic_trailing_comma=magic_trailing_comma)
    )
