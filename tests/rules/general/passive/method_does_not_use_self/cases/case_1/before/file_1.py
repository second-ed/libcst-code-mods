class Class:
    def __init__(self, thing: int) -> None:
        self.thing = thing

    def add(self, a: int, b: int) -> int:
        return a + b

    def method_uses_self_is_not_caught(self, arg: int) -> None:
        self.thing += arg


def add(a: int, b: int) -> int:
    return a + b
