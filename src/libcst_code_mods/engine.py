# repo-map-desc: main entrypoint to the code mods
from __future__ import annotations

from collections.abc import Collection
from pathlib import Path

import libcst as cst
from libcst.metadata import FullRepoManager

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING, RuleMapping, make_rule_mapping_immutable
from libcst_code_mods.utils import black_format


def multi_file_refactor(
    root: Path | str,
    paths: list[Path],
    refactoring_rules: list[RefactoringRule],
    rule_mapping: RuleMapping | None = None,
    specific_paths: Collection = (),
) -> dict[Path, str]:
    rule_mapping = rule_mapping if rule_mapping is not None else RULE_MAPPING
    immutable_rule_mapping = make_rule_mapping_immutable(rule_mapping)

    manager = get_manager(str(root))
    if specific_paths:
        paths = [p for p in paths if str(p) in specific_paths]

    contexts = {
        type(refactoring_rule): CstContext(refactoring_rule.to_dict()) for refactoring_rule in refactoring_rules
    }

    for refactoring_rule in refactoring_rules:
        cst_rule = immutable_rule_mapping[type(refactoring_rule)]
        if not cst_rule.visitor_factory:
            continue

        visitor = cst_rule.visitor_factory.from_context(contexts[type(refactoring_rule)])

        for path in paths:
            wrapper = manager.get_metadata_wrapper_for_path(str(path))
            wrapper.visit(visitor)

    refactored_code = {}

    for path in paths:
        wrapper = manager.get_metadata_wrapper_for_path(str(path))
        original_code = wrapper.module.code

        for refactoring_rule in refactoring_rules:
            cst_rule = immutable_rule_mapping[type(refactoring_rule)]
            module = wrapper.visit(cst_rule.transformer_factory.from_context(contexts[type(refactoring_rule)]))
            wrapper = cst.MetadataWrapper(module, cache=wrapper._cache)  # noqa: SLF001

        new_code = wrapper.module.code
        if new_code != original_code:
            refactored_code[path] = black_format(new_code)

    return refactored_code


def get_manager(root: str) -> FullRepoManager:
    return FullRepoManager(root, paths=list(map(str, Path(root).rglob("**/*.py"))), providers=METADATA_DEPS)
