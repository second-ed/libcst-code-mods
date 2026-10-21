from __future__ import annotations

import attrs

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor


@attrs.frozen
class CstRule:
    visitor_factory: type[BaseCstVisitor] | None = None
    transformer_factory: type[BaseCstTransformer] | None = None
