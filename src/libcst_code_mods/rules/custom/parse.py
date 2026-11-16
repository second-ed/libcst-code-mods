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
        CustomDiagnosticVisitor(
            path,
            context,
            rule=rule,
            matcher=_parse_matcher(conf["matcher"]),
            instead=conf.get("instead", f"No instead given for {rule}"),
            include=conf.get("include", ()),
            exclude=conf.get("exclude", ()),
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
