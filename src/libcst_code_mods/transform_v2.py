# repo-map-desc: main entrypoint to the code mods
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from types import MappingProxyType

import black
import libcst as cst
from libcst.metadata import FullRepoManager

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.core.cst_rule import CstRule
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import make_rule_mapping_immutable


def transform_code(
    root: str,
    path: str,
    refactorings: list[RefactoringRule],
    rule_mapping: defaultdict[type[RefactoringRule], dict[str, type[BaseCstTransformer | BaseCstVisitor]]],
) -> str:
    wrapper = get_manager(root).get_metadata_wrapper_for_path(path)
    immutable_rule_mapping = make_rule_mapping_immutable(rule_mapping)
    cache = wrapper._cache  # noqa: SLF001

    for rule in refactorings:
        module = apply_rule(wrapper, rule, immutable_rule_mapping)
        wrapper = cst.MetadataWrapper(module, cache=cache)

    return black.format_str(wrapper.module.code, mode=black.FileMode(line_length=120, magic_trailing_comma=False))


def apply_rule(
    wrapper: cst.MetadataWrapper,
    refactoring_rule: RefactoringRule,
    rule_mapping: MappingProxyType[type[RefactoringRule], CstRule],
) -> cst.Module:
    context = CstContext(refactoring_rule.to_dict())
    cst_rule = rule_mapping[type(refactoring_rule)]

    if cst_rule.visitor_factory:
        wrapper.visit(cst_rule.visitor_factory.from_context(context))

    return wrapper.visit(cst_rule.transformer_factory.from_context(context))


def get_manager(root: str) -> FullRepoManager:
    return FullRepoManager(root, paths=list(map(str, Path(root).rglob("**/*.py"))), providers=METADATA_DEPS)
