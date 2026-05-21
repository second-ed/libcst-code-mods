from types import MappingProxyType

from libcst_code_mods.core.cst_rule import CstRule
from libcst_code_mods.core.refactoring_rule import RefactoringRule

RULE_MAPPING: MappingProxyType[type[RefactoringRule], CstRule] = MappingProxyType({})
