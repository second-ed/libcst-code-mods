# repo-map-desc: main entrypoint to the code mods
from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import libcst as cst
from libcst.metadata import FullRepoManager

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.core.cst_rule import CstRule
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING, RuleMapping, make_rule_mapping_immutable
from libcst_code_mods.utils import black_format


def multi_file_refactor(
    root: Path | str,
    paths: list[Path],
    refactoring_rules: list[RefactoringRule],
    rule_mapping: RuleMapping | None = None,
    specific_paths: list[str] | None = None,
) -> dict[Path, str]:
    rule_mapping = rule_mapping if rule_mapping is not None else RULE_MAPPING
    immutable_rule_mapping: MappingProxyType[type[RefactoringRule], CstRule] = make_rule_mapping_immutable(rule_mapping)

    if specific_paths:
        paths = [p for p in paths if str(p) in specific_paths]

    manager = get_manager(str(root), paths)
    contexts: dict[type[RefactoringRule], CstContext] = {
        type(refactoring_rule): CstContext(data=refactoring_rule.to_dict()) for refactoring_rule in refactoring_rules
    }

    for path in paths:
        _collect_context(
            manager=manager,
            refactoring_rules=refactoring_rules,
            immutable_rule_mapping=immutable_rule_mapping,
            contexts=contexts,
            path=str(path),
        )

    refactored_code = {}

    for path in paths:
        str_path = str(path)
        wrapper = manager.get_metadata_wrapper_for_path(str_path)
        original_code = wrapper.module.code

        for refactoring_rule in refactoring_rules:
            rule_context = contexts[type(refactoring_rule)]

            if str_path not in rule_context.paths:
                continue

            cst_rule = immutable_rule_mapping[type(refactoring_rule)]

            module = wrapper.visit(cst_rule.transformer_factory.from_context(rule_context))
            wrapper = cst.MetadataWrapper(module, cache=wrapper._cache)  # noqa: SLF001

        new_code = wrapper.module.code
        if new_code != original_code:
            refactored_code[path] = black_format(new_code)

    return refactored_code


def _collect_context(
    manager: FullRepoManager,
    refactoring_rules: list[RefactoringRule],
    immutable_rule_mapping: MappingProxyType[type[RefactoringRule], CstRule],
    contexts: dict[type[RefactoringRule], CstContext],
    path: str,
) -> None:
    wrapper = manager.get_metadata_wrapper_for_path(path)

    visitors = [
        visitor_factory.from_context(path, contexts[type(rule)])
        for rule in refactoring_rules
        if (visitor_factory := immutable_rule_mapping[type(rule)].visitor_factory) is not None
    ]
    if visitors:
        wrapper.visit_batched(visitors)


def get_manager(root: str, paths: list[Path] | None = None) -> FullRepoManager:
    paths = paths if paths is not None else list(Path(root).rglob("**/*.py"))
    return FullRepoManager(root, paths=list(map(str, paths)), providers=METADATA_DEPS)
