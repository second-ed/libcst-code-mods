from types import SimpleNamespace


def test_catches_assertions_on_attr() -> None:
    obj = SimpleNamespace(a=1, b=2, thing=[1, 2, 3])

    assert obj.a == 1
    assert obj.b == 2
    assert obj.thing == [1, 2, 3]


def test_catches_assertions_on_subscripts() -> None:
    obj = {"a": 1, "b": 2, "thing": [1, 2, 3]}

    assert obj["a"] == 1
    assert obj["b"] == 2
    assert obj["thing"] == [1, 2, 3]
