import pprintpp



def update(o: object, **attrs) -> None:
    for name, value in attrs.items():
        assert hasattr(o, name)
        setattr(o, name, value)


def repr(o: object) -> str:
    return type(o).__qualname__ + pprintpp.pformat(o.__dict__)
