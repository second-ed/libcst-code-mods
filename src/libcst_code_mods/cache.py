import hashlib
import json
from pathlib import Path
from typing import Self

import attrs

from libcst_code_mods.config import RefactoringConfig


@attrs.define
class RefactoringCache:
    cache_path: Path
    entries: dict[str, str]
    config_md5: str
    paths_to_process: list[Path]
    all_paths: list[Path]

    @classmethod
    def new(cls, config: RefactoringConfig, paths: list[Path], cache_path: Path | None = None) -> Self:
        if cache_path is None:
            cache_path = Path.cwd() / ".libcst_code_mods_cache" / "cache.json"

        config_md5 = _json_md5(config.to_dict())
        entries = _read_cache(cache_path) if config.fix else {}
        cached_md5_by_path = entries if entries.get("refactoring-rules-config.yaml") == config_md5 else {}

        return cls(
            cache_path=cache_path,
            entries=entries,
            config_md5=config_md5,
            paths_to_process=[path for path in paths if cached_md5_by_path.get(str(path.resolve())) != _path_md5(path)],
            all_paths=paths.copy(),
        )

    def update(self) -> None:
        updated_md5_by_path = self.entries.copy()
        updated_md5_by_path["refactoring-rules-config.yaml"] = self.config_md5
        updated_md5_by_path.update({str(path.resolve()): _path_md5(path) for path in self.all_paths})
        _write_cache(self.cache_path, updated_md5_by_path)


def _md5(value: bytes) -> str:
    return hashlib.md5(value, usedforsecurity=False).hexdigest()


def _path_md5(path: Path) -> str:
    return _md5(path.read_bytes())


def _json_md5(value: dict) -> str:
    encoded_value = json.dumps(value, sort_keys=True).encode("utf-8")
    return _md5(encoded_value)


def _read_cache(cache_path: Path) -> dict[str, str]:
    if not cache_path.is_file():
        return {}

    try:
        cache = json.loads(cache_path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(cache, dict):
        return {}
    return {path: digest for path, digest in cache.items() if isinstance(path, str) and isinstance(digest, str)}


def _write_cache(cache_path: Path, md5_by_path: dict[str, str]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    (cache_path.parent / ".gitignore").write_text("# Automatically created by libcst_code_mods.\n*\n")
    cache_path.write_text(json.dumps(md5_by_path, indent=4, sort_keys=True) + "\n")
