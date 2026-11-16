from collections.abc import Collection
from typing import Any

import libcst.matchers as m


def _parse_matcher(config: dict[str, Any]) -> m.BaseMatcherNode:
    matcher_name = config["type"]
    matcher_type = getattr(m, matcher_name)

    if matcher_name == "OneOf":
        return matcher_type(*(_parse_value(item) for item in config["options"]))

    kwargs = {name: _parse_value(value) for name, value in config.items() if name != "type"}

    return matcher_type(**kwargs)


def _parse_value(value: Collection) -> m.BaseMatcherNode | list[m.BaseMatcherNode]:
    if isinstance(value, dict):
        return _parse_matcher(value)

    if isinstance(value, list):
        return list(map(_parse_value, value))

    return value
