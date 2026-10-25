import libcst as cst

from libcst_code_mods.cst_builders.primitives import cst_register


def _cst_call(name: str, args: list[cst.BaseElement] | None = None) -> cst.Call:
    args = args or []
    function: cst.BaseExpression = cst.Name(name.split(".", 1)[0])

    for part in name.split(".")[1:]:
        function = cst.Attribute(value=function, attr=cst.Name(part))

    return cst.Call(function, [cst.Arg(arg) for arg in args])


@cst_register("ContextManager")
def cst_nullcontext() -> cst.Call:
    return _cst_call("nullcontext")
