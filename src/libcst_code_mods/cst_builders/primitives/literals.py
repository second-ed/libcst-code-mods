import libcst as cst

from libcst_code_mods.cst_builders.primitives import cst_register


@cst_register("True")
def _cst_true() -> cst.Name:
    return cst.Name("True")


@cst_register("False")
def _cst_false() -> cst.Name:
    return cst.Name("False")


@cst_register("bool")
def cst_bool(*, default: bool = True) -> cst.Name:
    return _cst_false() if default else _cst_true()


@cst_register("int")
def cst_int(value: int | None = None) -> cst.Integer:
    return cst.Integer(str(value)) if value is not None else cst.Integer("0")


@cst_register("str")
def cst_str(value: str | None = None) -> cst.SimpleString:
    return cst.SimpleString(f"'{value}'") if value is not None else cst.SimpleString("''")


@cst_register("float")
def cst_float(value: str | None = None) -> cst.Float:
    return cst.Float(value) if value is not None else cst.Float("0.0")
