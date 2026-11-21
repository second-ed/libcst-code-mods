from abc import abstractmethod


class Class:
    def __init__(self, thing: int) -> None:
        self.thing = thing

    def add(self, a: int, b: int) -> int:
        return a + b

    def method_uses_self_is_not_caught(self, arg: int) -> None:
        self.thing += arg

    @abstractmethod
    def some_abstract_method(self, a: str) -> str: ...

    @custom_dec
    @abstractmethod
    def some_decorated_abstract_method(self, a: str) -> str: ...


def add(a: int, b: int) -> int:
    return a + b
