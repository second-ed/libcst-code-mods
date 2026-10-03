import libcst as cst
import libcst.matchers as m


def make_decorator_arg_true(decorator: cst.Decorator, arg_name: str) -> cst.Decorator:
    if m.matches(decorator, m.Decorator(decorator=m.OneOf(m.Name(), m.Attribute()))):
        call = cst.Call(func=decorator.decorator, args=[cst.Arg(keyword=cst.Name(arg_name), value=cst.Name("True"))])
        return decorator.with_changes(decorator=call)

    if (matched := m.extract(decorator, m.Decorator(decorator=m.SaveMatchedNode(m.Call(), "call")))) is None:
        return decorator

    call: cst.Call = matched["call"]

    return decorator.with_changes(decorator=call.with_changes(args=extract_args(call, arg_name)))


def extract_args(call: cst.Call, arg_name: str) -> list[cst.Arg]:
    if any(m.matches(arg, m.Arg(keyword=m.Name(arg_name), value=m.DoNotCare())) for arg in call.args):
        return [
            (
                arg.with_changes(value=cst.Name("True"))
                if m.matches(arg, m.Arg(keyword=m.Name(arg_name), value=m.DoNotCare()))
                else arg
            )
            for arg in call.args
        ]
    return [*call.args, cst.Arg(keyword=cst.Name(arg_name), value=cst.Name("True"))]
