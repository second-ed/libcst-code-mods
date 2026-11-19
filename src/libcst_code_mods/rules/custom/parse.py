from collections.abc import Collection
from typing import Any

import libcst.matchers as m

from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.rules.custom.visitor import CustomDiagnosticVisitor


def parse_custom_rule_visitors(config: dict, path: str, context: CstContext) -> list[CustomDiagnosticVisitor]:
    """Example:

    ```yaml
    custom_rules:
        no_print:
            include:
            - "src/**/*.py"
            exclude:
            - "src/generated/**"
            - "src/**/test_*.py"
            matcher:
            type: Call
            func:
                type: Name
                value: print
            instead: "use the project logger"
    ```

    This function expects the values under the "custom_rules" key
    """
    return [
        CustomDiagnosticVisitor.new(
            path,
            context,
            rule=rule,
            matcher=_parse_matcher(conf["matcher"]),
            instead=conf.get("instead", f"No instead given for {rule}"),
            include=conf.get("include", ()),
            exclude=conf.get("exclude", ()),
            matcher_name=conf["matcher"]["type"],
        )
        for rule, conf in config.items()
    ]


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


def _matcher_to_dict(matcher: m.BaseMatcherNode) -> dict[str, object]:
    """Convert a LibCST matcher into the dictionary form used by custom rules."""
    if not isinstance(matcher, m.BaseMatcherNode):
        raise TypeError(f"Expected a LibCST matcher, got {type(matcher).__name__}")

    values = {name: _matcher_value_to_dict(value) for name, value in _matcher_fields(matcher).items()}
    return {"type": type(matcher).__name__, **values}


def _matcher_fields(matcher: m.BaseMatcherNode) -> dict[str, object]:
    if isinstance(matcher, m.OneOf):
        return {"options": matcher.options}

    fields = getattr(matcher, "__dict__", {})
    return {name: value for name, value in fields.items() if not name.startswith("_") and value is not m.DoNotCare()}


def _matcher_value_to_dict(value: object) -> object:
    if value is m.DoNotCare():
        return None
    if isinstance(value, m.BaseMatcherNode):
        return _matcher_to_dict(value)
    if isinstance(value, (list, tuple)):
        return list(map(_matcher_value_to_dict, value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Cannot convert matcher value of type {type(value).__name__}")
