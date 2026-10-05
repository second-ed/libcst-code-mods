from __future__ import annotations

from collections.abc import Collection, Iterator, Sequence
from pathlib import Path
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import CodeRange, PositionProvider

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.core.diagnostics import AggregatedDiagnostic, Diagnostic
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

MIN_BLOCK_SIZE = 2
# WET
MIN_OCCURRENCES = 3


@register_rule
@attrs.define(frozen=True)
class IdentifyDuplicatedCode(RefactoringRule):
    min_block_size: int = 2
    max_block_size: int = 5
    top_n: int | None = None
    min_occurrences: int = MIN_OCCURRENCES

    def __attrs_post_init__(self) -> None:
        errs = []
        if self.min_block_size < MIN_BLOCK_SIZE:
            errs.append(f"{self.min_block_size = } must be at least {MIN_BLOCK_SIZE}")
        if self.max_block_size < self.min_block_size:
            errs.append(f"{self.max_block_size = } must be at least {self.min_block_size = }")
        if self.top_n is not None and self.top_n < 1:
            errs.append(f"{self.top_n = } must be at least 1")
        if errs:
            raise ValueError(f"Invalid args: {errs}")


@register_rule_visitor(IdentifyDuplicatedCode)
@attrs.define
class IdentifyDuplicatedCodeVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    min_block_size: int
    max_block_size: int
    top_n: int | None
    min_occurrences: int

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        for candidates in _iter_candidates(node.body):
            self._collect_candidate_blocks(candidates)

    def _collect_candidate_blocks(self, candidate: cst.IndentedBlock) -> None:
        statements = list(candidate.body)
        n_statements = len(statements)

        for block_size in range(self.min_block_size, min(self.max_block_size, n_statements) + 1):
            for start in range(n_statements - block_size + 1):
                block = tuple(statements[start : start + block_size])
                extraction_status, extraction_reason = _extraction_status(block)
                if not extraction_status:
                    continue
                diagnostic = Diagnostic(
                    "identify_duplicated_code",
                    Path(self.path).relative_to(self.context.root),
                    _code_range(self, block),
                    cst.Module(body=list(block)).code,
                )
                (
                    self.context.data.setdefault("duplicated_code_blocks", {})
                    .setdefault((_fingerprint(block), block_size), [])
                    .append((diagnostic, extraction_status, extraction_reason))
                )
                self.context.paths.add(self.path)

    @classmethod
    def finalize_context(cls, rule: RefactoringRule, context: CstContext) -> list[AggregatedDiagnostic]:
        if not isinstance(rule, IdentifyDuplicatedCode):
            raise TypeError(
                f"IdentifyDuplicatedCodeVisitor requires an IdentifyDuplicatedCode rule object. Got: {rule = }"
            )

        groups: dict[tuple[str, int], list[tuple[Diagnostic, bool, str | None]]] = context.data.get(
            "duplicated_code_blocks", {}
        )

        agg_diagnostics = []

        for (fingerprint, block_size), entries in groups.items():
            if len(entries) < rule.min_occurrences:
                continue

            agg_diagnostics.append(
                AggregatedDiagnostic(
                    rule="identify_duplicated_code",
                    fingerprint=fingerprint,
                    block_size=block_size,
                    diagnostics=tuple(entry[0] for entry in entries),
                    extractable=all(entry[1] for entry in entries),
                    extraction_reason=next((entry[2] for entry in entries if entry[2]), None),
                )
            )

        agg_diagnostics.sort(
            key=lambda diagnostic: (-len(diagnostic.diagnostics), -diagnostic.block_size, diagnostic.fingerprint)
        )
        if top_n := context.data.get("top_n"):
            agg_diagnostics = agg_diagnostics[:top_n]
        return agg_diagnostics


@register_rule_transformer(IdentifyDuplicatedCode)
@attrs.define
class IdentifyDuplicatedCodeTransformer(BaseCstTransformer):
    pass


def _iter_candidates(node: cst.CSTNode) -> Iterator[cst.IndentedBlock]:
    if isinstance(node, (cst.FunctionDef, cst.ClassDef)):
        return
    if isinstance(node, cst.IndentedBlock):
        yield node
    for child in node.children:
        if isinstance(child, cst.CSTNode):
            yield from _iter_candidates(child)


def _code_range(visitor: BaseCstVisitor, block: tuple[cst.BaseStatement, ...]) -> CodeRange:
    start = visitor.get_metadata(PositionProvider, block[0])
    end = visitor.get_metadata(PositionProvider, block[-1])
    return CodeRange(start=start.start, end=end.end)


def _fingerprint(block: tuple[cst.BaseStatement, ...]) -> str:
    collector = _NameUsageCollector()
    for statement in block:
        statement.visit(collector)

    transformed = cst.Module(body=list(block)).visit(
        _FingerprintTransformer(collector.call_target_ids, collector.keyword_ids, collector.attribute_ids)
    )
    return transformed.code


def _extraction_status(block: tuple[cst.BaseStatement, ...]) -> tuple[bool, str | None]:
    module = cst.Module(body=list(block))
    returns = m.findall(module, m.Return())
    if returns and not _has_single_final_return(block, returns):
        return False, "The block contains a nested or non-final return statement."
    if m.findall(module, m.Yield()):
        return False, "The block contains a yield statement."
    if m.findall(module, m.OneOf(m.Break(), m.Continue())) and not any(
        isinstance(statement, (cst.For, cst.While)) for statement in block
    ):
        return False, "The block contains break or continue without its owning loop."
    return True, None


def _has_single_final_return(block: tuple[cst.BaseStatement, ...], returns: Sequence[cst.Return]) -> bool:
    if len(returns) != 1 or not isinstance(block[-1], cst.SimpleStatementLine):
        return False
    return any(isinstance(statement, cst.Return) for statement in block[-1].body)


@attrs.define
class _NameUsageCollector(cst.CSTVisitor):
    call_target_ids: set[int] = attrs.field(factory=set)
    keyword_ids: set[int] = attrs.field(factory=set)
    attribute_ids: set[int] = attrs.field(factory=set)

    def visit_Call(self, node: cst.Call) -> bool:  # noqa: N802
        if isinstance(node.func, cst.Name):
            self.call_target_ids.add(id(node.func))
        elif isinstance(node.func, cst.Attribute):
            self.call_target_ids.add(id(node.func.attr))
        return True

    def visit_Arg(self, node: cst.Arg) -> bool:  # noqa: N802
        if node.keyword is not None:
            self.keyword_ids.add(id(node.keyword))
        return True

    def visit_Attribute(self, node: cst.Attribute) -> bool:  # noqa: N802
        self.attribute_ids.add(id(node.attr))
        return True


@attrs.define
class _FingerprintTransformer(cst.CSTTransformer):
    call_target_ids: set[int]
    keyword_ids: set[int]
    attribute_ids: set[int]
    names: dict[str, str] = attrs.field(factory=dict)

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:  # noqa: N802
        if id(original_node) in self.call_target_ids or id(original_node) in self.keyword_ids:
            return updated_node
        if id(original_node) in self.attribute_ids:
            self.names.setdefault(original_node.value, f"__name_{len(self.names)}__")
            return updated_node
        if original_node.value in {"True", "False"}:
            return cst.Name("__literal_boolean__")
        if original_node.value == "None":
            return cst.Name("__literal_none__")
        return cst.Name(self.names.setdefault(original_node.value, f"__name_{len(self.names)}__"))

    def leave_Integer(self, _original_node: cst.Integer, _updated_node: cst.Integer) -> cst.Name:  # noqa: N802
        return cst.Name("__literal_integer__")

    def leave_Float(self, _original_node: cst.Float, _updated_node: cst.Float) -> cst.Name:  # noqa: N802
        return cst.Name("__literal_float__")

    def leave_SimpleString(  # noqa: N802
        self, original_node: cst.SimpleString, _updated_node: cst.SimpleString
    ) -> cst.Name:
        kind = "bytes" if original_node.value.lower().startswith(("b'", 'b"', "br'", 'br"', "rb'", 'rb"')) else "string"
        return cst.Name(f"__literal_{kind}__")

    def leave_FormattedString(  # noqa: N802
        self, _original_node: cst.FormattedString, _updated_node: cst.FormattedString
    ) -> cst.Name:
        return cst.Name("__literal_fstring__")
