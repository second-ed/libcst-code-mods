from collections import defaultdict
from collections.abc import Callable
from types import MappingProxyType

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_rule import CstRule
from libcst_code_mods.core.refactoring_rule import RefactoringRule

RULE_MAPPING: defaultdict[type[RefactoringRule], dict[str, type[BaseCstTransformer] | type[BaseCstVisitor]]] = (
    defaultdict(dict)
)


def make_rule_mapping_immutable(
    rule_mapping: defaultdict[type[RefactoringRule], dict[str, type[BaseCstTransformer] | type[BaseCstVisitor]]],
) -> MappingProxyType[type[RefactoringRule], CstRule]:
    return MappingProxyType({k: CstRule(**v) for k, v in rule_mapping.items()})


def register_rule_transformer(
    rule: type[RefactoringRule],
) -> Callable[..., type[BaseCstTransformer] | type[BaseCstVisitor]]:
    def wrapper(
        cls: type[BaseCstTransformer] | type[BaseCstVisitor],
    ) -> type[BaseCstTransformer] | type[BaseCstVisitor]:
        RULE_MAPPING[rule]["transformer_factory"] = cls
        return cls

    return wrapper


def register_rule_visitor(
    rule: type[RefactoringRule],
) -> Callable[..., type[BaseCstTransformer] | type[BaseCstVisitor]]:
    def wrapper(
        cls: type[BaseCstTransformer] | type[BaseCstVisitor],
    ) -> type[BaseCstTransformer] | type[BaseCstVisitor]:
        RULE_MAPPING[rule]["visitor_factory"] = cls
        return cls

    return wrapper
