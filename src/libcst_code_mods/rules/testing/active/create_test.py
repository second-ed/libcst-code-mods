import attrs

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule


# @register_rule
@attrs.define(frozen=True)
class CreateTest(RefactoringRule):
    function_names: list[str]


# @register_rule_visitor(CreateTest)
@attrs.define
class CreateTestVisitor(BaseCstVisitor):
    pass


# @register_rule_transformer(CreateTest)
@attrs.define
class CreateTestTransformer(BaseCstTransformer):
    pass
