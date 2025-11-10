# test_multidispatch.py

from __future__ import annotations

import warnings

import pytest

from multiarg_dispatch import DispatchWarning, multidispatch


# -------------------
# Fixture for the generic function
# -------------------
@pytest.fixture
def test_func_fixture():
    @multidispatch
    def test_func(a, b=None):
        return "default"

    @test_func.register
    def _(a: int, b: str = "default") -> str:
        return f"int:{a},str:{b}"

    @test_func.register
    def _(a: str, b: list = []) -> str:
        if b is None:
            b = []
        return f"str:{a},list:{b}"

    @test_func.register
    def _(a: float, b: str | list = "default") -> str:
        return f"float:{a},union:{b}"

    return test_func


# -------------------
# Default dispatch
# -------------------
def test_default_dispatch(test_func_fixture):
    result = test_func_fixture(object())
    assert result == "default"


# -------------------
# Int dispatch
# -------------------
def test_int_dispatch(test_func_fixture):
    assert test_func_fixture(5) == "int:5,str:default"
    assert test_func_fixture(5, "hello") == "int:5,str:hello"


# -------------------
# Str dispatch
# -------------------
def test_str_dispatch(test_func_fixture):
    assert test_func_fixture("abc") == "str:abc,list:[]"
    assert test_func_fixture("xyz", ["x", "y"]) == "str:xyz,list:['x', 'y']"


# -------------------
# Float dispatch with union
# -------------------
def test_float_union_dispatch(test_func_fixture):
    assert test_func_fixture(3.14) == "float:3.14,union:default"
    assert test_func_fixture(2.71, "extra") == "float:2.71,union:extra"
    assert test_func_fixture(1.618, ["a", "b"]) == "float:1.618,union:['a', 'b']"


# -------------------
# Keyword arguments
# -------------------
def test_keyword_arguments_dispatch(test_func_fixture):
    assert test_func_fixture(a=10, b="kw") == "int:10,str:kw"
    assert test_func_fixture(a="hello", b=["kw"]) == "str:hello,list:['kw']"
    assert test_func_fixture(a=2.0, b=["kw"]) == "float:2.0,union:['kw']"


# -------------------
# Default parameter warning
# -------------------
def test_default_parameter_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @multidispatch
        def f(x):
            return x

        @f.register
        def _(x: int = 5) -> int:
            return x

        _ = f(10)
        assert any(issubclass(warning.category, DispatchWarning) for warning in w)


# -------------------
# Missing type hints
# -------------------
def test_missing_type_hints_error(test_func_fixture):
    with pytest.raises(TypeError):

        @test_func_fixture.register
        def _(x, y):  # no type hints
            return x


# -------------------
# Empty call
# -------------------
def test_empty_call_raises_typeerror(test_func_fixture):
    with pytest.raises(TypeError):
        test_func_fixture()


# -------------------
# Union type dispatch
# -------------------
def test_union_type_dispatch():
    @multidispatch
    def f(x):
        return "default"

    @f.register
    def _(x: int | float) -> str:
        return "number"

    assert f(10) == "number"
    assert f(3.14) == "number"
    assert f("str") == "default"


# -------------------
# Garbage collection test
# -------------------
def test_registered_class_garbage_collection():
    """Test that registered classes are kept alive by the registry and can be collected when the function is deleted."""
    import gc
    import weakref

    @multidispatch
    def process(obj):
        return "default"

    # Create a dynamic class to register
    DynamicAnimal = type("DynamicAnimal", (), {})

    # Create a weak reference to track if it gets collected
    weak_ref = weakref.ref(DynamicAnimal)

    # Register using __annotations__ directly to avoid string resolution issues
    def _impl(obj):
        return "dynamic_animal"

    _impl.__annotations__ = {"obj": DynamicAnimal, "return": str}
    process.register(_impl)

    # Verify the class works
    instance = DynamicAnimal()
    result = process(instance)
    assert result == "dynamic_animal"
    del instance

    # At this point, DynamicAnimal should still be alive because it's in the registry
    gc.collect()
    assert weak_ref() is not None, (
        "DynamicAnimal should still be alive (kept by registry)"
    )

    # Delete the local reference to DynamicAnimal
    del DynamicAnimal
    gc.collect()

    # Still should be alive because the registry holds a reference
    assert weak_ref() is not None, (
        "DynamicAnimal should still be alive (kept by registry)"
    )

    # Now delete the process function (which holds the registry) and the implementation
    del _impl
    del process
    gc.collect()

    # Now the class should be garbage collected
    assert weak_ref() is None, (
        "DynamicAnimal should be garbage collected after process function is deleted"
    )
