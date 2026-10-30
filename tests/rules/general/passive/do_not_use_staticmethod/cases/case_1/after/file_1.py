class SomeClass:
    @staticmethod
    def should_catch_this_staticmethod(x: int, y: int) -> int:
        return x + y

    def should_not_flag_this_instance_method(self, x: int, y: int) -> int:
        return x + y

    @classmethod
    def should_not_flag_this_classmethod(cls, x: int, y: int) -> int:
        return x + y
