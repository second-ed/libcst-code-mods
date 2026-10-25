import libcst as cst

from libcst_code_mods.cst_builders.primitives import cst_register


@cst_register("tuple")
def cst_tuple(values: list[cst.BaseExpression] | None = None) -> cst.Tuple:
    return cst.Tuple([cst.Element(value) for value in values]) if values is not None else cst.Tuple([])


@cst_register("list")
def cst_list(values: list[cst.BaseExpression] | None = None) -> cst.List:
    return cst.List([cst.Element(value) for value in values]) if values is not None else cst.List([])


@cst_register("dict")
def cst_dict(values: list[cst.BaseDictElement] | None = None) -> cst.Dict:
    return cst.Dict(values) if values is not None else cst.Dict([])


@cst_register("set")
def cst_set(values: list[cst.BaseExpression] | None = None) -> cst.Set | cst.Call:
    return cst.Set([cst.Element(value) for value in values]) if values is not None else cst.Call(cst.Name("set"))
