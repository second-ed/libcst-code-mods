import re
import sys
from pathlib import Path

import attrs
import libcst as cst
import libcst.matchers as m
import polars as pl

from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.utils import black_format

END_MARKER = "---"
EXAMPLES_RE = re.compile(rf"\n*Examples:\n.*?^\s*{END_MARKER}\s*$", re.MULTILINE | re.DOTALL)
DOC_TEMP = """Case
----

Pre-transformer:

.. code-block:: python

{before_code}

Post-transformer:

.. code-block:: python

{after_code}
"""


def main(src_root: Path = REPO_ROOT / "src/libcst_code_mods/rules", test_root: Path = REPO_ROOT / "tests/rules") -> int:
    src_df = (
        _paths_to_df(src_root)
        .pipe(_add_domain_and_active_cols)
        .with_columns(rule_name=pl.col("basename").str.strip_suffix(".py"))
    )

    tests_df = (
        _paths_to_df(test_root)
        .filter(pl.col("path_parts").list.len() > 1)
        .pipe(_add_domain_and_active_cols)
        .with_columns(before_or_after=pl.col("path_parts").list.get(-2), rule_name=pl.col("path_parts").list.get(2))
        .filter(pl.col("basename").is_in(["file_1.py", "file_2.py"]))
        .select("rule_name", "basename", "before_or_after", "path")
        .pivot(on="before_or_after", index=["rule_name", "basename"], values="path")
        .select("rule_name", "before", "after")
    )

    df = (
        tests_df.join(src_df, on="rule_name", how="left", suffix="_src")
        .with_columns(
            before_code=pl.col("before").map_elements(_read_code, pl.String()),
            after_code=pl.col("after").map_elements(_read_code, pl.String()),
        )
        .with_columns(before_after=pl.struct(pl.col("before_code"), pl.col("after_code")))
        .with_columns(examples=pl.col("before_after").map_elements(create_examples, pl.List(pl.String())))
        .group_by("path")
        .agg(pl.col("examples").list.explode(empty_as_null=False, keep_nulls=False))
        .with_columns(pl.col("examples").list.join("\n\n"))
        .filter(pl.col("examples") != "")
    )

    exit_int = 0

    for row in df.iter_rows(named=True):
        path = Path(row["path"])
        tree = cst.parse_module(path.read_text())
        original_code = tree.code
        updated_code = tree.visit(_AddDocstringExamples(row["examples"])).code
        if black_format(original_code) != black_format(updated_code):
            path.write_text(f"{updated_code.strip()}\n")
            print(f"Modified {path.relative_to(REPO_ROOT)}")  # noqa: T201
            exit_int += 1

    return exit_int


def _paths_to_df(root: Path) -> pl.DataFrame:
    return (
        pl.DataFrame({"path": map(str, root.rglob("*.py"))})
        .with_columns(rule_path=pl.col("path").str.strip_prefix(str(root)).str.strip_chars("/"))
        .with_columns(path_parts=pl.col("rule_path").str.split("/"))
        .with_columns(basename=pl.col("path_parts").list.get(-1))
        .filter(~pl.col("basename").str.starts_with("_"))
    )


def _add_domain_and_active_cols(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(domain=pl.col("path_parts").list.get(0), active=pl.col("path_parts").list.get(1))


def _read_code(path: str) -> str:
    return Path(path).read_text()


def create_examples(struct: dict[str, str]) -> list[str]:
    changes = _add_indent_to_examples(_get_changed_code(struct))
    return [_add_indent(DOC_TEMP.format(**v)) for v in changes.values()]


def _get_changed_code(struct: dict[str, str]) -> dict[str, dict[str, str]]:
    diffs = _fn_diffs(struct)
    return {
        fn_name: code_states
        for fn_name, code_states in diffs.items()
        if code_states.get("before_code", f"no code for {fn_name}")
        != code_states.get("after_code", f"no code for {fn_name}")
    }


def _add_indent_to_examples(changes: dict[str, dict[str, str]], indent: str = "    ") -> dict[str, dict[str, str]]:
    indented = {}
    for fn_name, code_states in changes.items():
        for state, code in code_states.items():
            indented.setdefault(fn_name, {})[state] = _add_indent(code, indent)
    return indented


def _add_indent(code: str, indent: str = "    ") -> str:
    return "\n".join((indent + line).rstrip() for line in code.splitlines())


def _fn_diffs(struct: dict[str, str]) -> dict[str, dict[str, str]]:
    visitor = _FnVisitor()

    for state in ["before_code", "after_code"]:
        visitor.state = state
        tree = cst.parse_module(struct[state])
        tree.visit(visitor)
    return visitor.fns


@attrs.define
class _FnVisitor(cst.CSTVisitor):
    state: str = attrs.field(default="")
    fns: dict[str, dict[str, str]] = attrs.field(factory=dict)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        self.fns.setdefault(node.name.value, {})[self.state] = normalise(node).strip()
        return super().visit_FunctionDef(node)


@attrs.define
class _AddDocstringExamples(BaseCstTransformer):
    examples: str
    decorator: str = "register_rule"

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:  # noqa: N802 ARG002
        if not any(m.matches(d.decorator, m.Name(self.decorator)) for d in updated_node.decorators):
            return updated_node

        body = list(updated_node.body.body)

        examples_block = f"Examples:\n\n{self.examples}\n{END_MARKER}\n"

        if (
            body
            and isinstance(body[0], cst.SimpleStatementLine)
            and len(body[0].body) == 1
            and isinstance(body[0].body[0], cst.Expr)
            and isinstance(body[0].body[0].value, cst.SimpleString)
        ):
            existing_docstring = body[0].body[0].value.evaluated_value
            existing_docstring = EXAMPLES_RE.sub("", existing_docstring).rstrip()

            new_docstring = f"{existing_docstring}\n\n{examples_block}" if existing_docstring else examples_block
            str_marker = self.get_str_marker(new_docstring)
            body[0] = cst.SimpleStatementLine(
                body=[cst.Expr(cst.SimpleString(value=f"{str_marker}{new_docstring}{str_marker}"))]
            )
        else:
            str_marker = self.get_str_marker(examples_block)
            body.insert(
                0,
                cst.SimpleStatementLine(
                    body=[cst.Expr(cst.SimpleString(value=f"{str_marker}{examples_block}{str_marker}"))]
                ),
            )

        return updated_node.with_changes(body=updated_node.body.with_changes(body=body))

    def get_str_marker(self, docstring: str) -> str:
        return '"""' if '"""' not in docstring else "'''"


if __name__ == "__main__":
    sys.exit(main())
