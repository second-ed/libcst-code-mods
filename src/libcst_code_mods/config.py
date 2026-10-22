from pathlib import Path
from typing import Any, Self

import attrs
import yaml

CONFIG_FILENAME = "refactoring-rules-config.yaml"


@attrs.frozen
class RefactoringConfig:
    rules: dict[str, Any]
    fix: bool = True
    black_format: bool = False

    @classmethod
    def from_file(
        cls,
        config_path: Path | str | None = None,
        *,
        fix: bool,
        black_format: bool | None = None,
        rule_names: list[str] | None = None,
    ) -> Self:
        path = _resolve_config_path(config_path)
        values = yaml.safe_load(path.read_text()) or {}
        configured_rules = values.get("rules", {})
        return cls(
            rules=(
                {name: configured_rules.get(name, {}) for name in rule_names}
                if rule_names is not None
                else configured_rules
            ),
            fix=fix,
            black_format=black_format if black_format is not None else values.get("black_format", False),
        )

    def to_dict(self) -> dict:
        return attrs.asdict(self)


def _resolve_config_path(config_path: Path | str | None) -> Path:
    if config_path is not None:
        return Path(config_path)

    cwd_config_path = Path.cwd() / CONFIG_FILENAME
    if cwd_config_path.is_file():
        return cwd_config_path

    raise FileNotFoundError(f"No config file was supplied and the current directory does not contain {CONFIG_FILENAME}")
