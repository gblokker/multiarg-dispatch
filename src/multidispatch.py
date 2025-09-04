# type: ignore

import inspect
import types
import warnings
from abc import get_cache_token
from functools import update_wrapper
from typing import Union, get_args, get_origin, get_type_hints


class DispatchWarning(UserWarning):
    """Warning raised when dispatching might be affected by defaults."""


def _is_union_type(cls):
    return get_origin(cls) in {Union, types.UnionType}


def _is_valid_dispatch_type(cls):
    if isinstance(cls, type):
        return True
    return _is_union_type(cls) and all(isinstance(arg, type) for arg in get_args(cls))


def _find_impl(arg_types: tuple, registry):
    """Find the best matching implementation for a given set of argument types."""
    for registered_types, func in registry.items():
        if registered_types is object:
            continue  # Skip the default implementation
        print(type(registered_types), registered_types, type(arg_types), arg_types)
        if len(arg_types) != len(registered_types):
            continue  # Skip if the number of arguments doesn't match
        if all(issubclass(arg, reg) for arg, reg in zip(arg_types, registered_types)):
            print("MATCH", arg_types, registered_types, func)
            return func
    return registry.get(object)  # Fallback to the default implementation


def singledispatch(func):
    """Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviors depending upon the type of its first argument. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.
    """
    registry = {}
    cache_token = None
    n_arguments = len(inspect.signature(func).parameters)

    def dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to return the best available implementation
        for the given *cls* registered on *generic_func*.
        """
        nonlocal cache_token
        if cache_token is not None:
            current_token = get_cache_token()
            if cache_token != current_token:
                cache_token = current_token
        try:
            impl = registry[cls]
        except KeyError:
            impl = _find_impl(cls, registry)
        return impl

    def register(func=None):
        """generic_func.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_func*.
        """
        nonlocal cache_token

        type_hints = get_type_hints(func)
        sig = inspect.signature(func)
        if len(type_hints) != len(sig.parameters):
            raise TypeError(
                f"All arguments must be type-annotated for {funcname!r}. "
                f"Got {len(type_hints)} annotations for {len(sig.parameters)} parameters."
            )
        for name, param in sig.parameters.items():
            if param.default is not inspect._empty:
                warnings.warn(
                    f"Parameter '{name}' has a default value ({param.default}).\n "
                    f"Note that default values are not considered in dispatching when calling the function.",
                    category=DispatchWarning,
                )
        for argname, cls in type_hints.items():
            if not _is_valid_dispatch_type(cls):
                if _is_union_type(cls):
                    raise TypeError(
                        f"Invalid annotation for {argname!r}. "
                        f"{cls!r} not all arguments are classes."
                    )
                else:
                    raise TypeError(
                        f"Invalid annotation for {argname!r}. {cls!r} is not a class."
                    )

        clss = []
        for _argname, cls in type_hints.items():
            cls_union = []
            if _is_union_type(cls):
                for arg in get_args(cls):
                    cls_union.append(arg)
                clss.append(tuple(cls_union))
            else:
                clss.append(cls)

        if n_arguments != len(clss):
            raise TypeError(
                f"Cannot register {func!r} for types {clss}. "
                f"Expected {n_arguments} types."
            )

        registry[tuple(clss)] = func

        if cache_token is None and hasattr(cls, "__abstractmethods__"):
            cache_token = get_cache_token()
        return func

    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f"{funcname} requires at least 1 positional argument")
        cls_args = [arg.__class__ for arg in args]

        if kw is not None:
            cls_kw = [type(value) for value in kw.values()]
            cls_args.extend(cls_kw)
        return dispatch(tuple(cls_args))(*args, **kw)

    funcname = getattr(func, "__name__", "singledispatch function")
    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    update_wrapper(wrapper, func)
    return wrapper


# Define a generic function
@singledispatch
def greet(value, extra=None):
    print(f"Hello, {value}! Extra: {extra}")


# Register a specific implementation for `int`
@greet.register
def _(value: int, extra: str = "default"):
    print(f"Hello, number {value}! Extra: {extra}")


# Register a specific implementation for `str`
@greet.register
def _(value: str, extra: list = None):
    if extra is None:
        extra = []
    print(f"Hello, {value.capitalize()}! Extra: {', '.join(map(str, extra))}")


# Register a specific implementation for `list`
@greet.register
def _(value: list, extra: dict = None):
    if extra is None:
        extra = {}
    print("Hello, everyone!")
    for item in value:
        print(f"- {item}")
    print(f"Extra: {extra}")


@greet.register
def _(value: float, extra: int = 0):
    print(f"Hello, float {value} with extra {extra}!")


# Test the generic function with various types
greet("world")  # Output: Hello, World! Extra:
greet(42, "hiiiii")  # Output: Hello, number 42! Extra: default
greet(
    ["Alice", "Bob", "Charlie"], {"group": "friends"}
)  # Output: Hello, everyone! (and lists names with extra)
greet(3.14)  # Output: Hello, float 3.14 with extra 0!
greet(2.71, 5)  # Output: Hello, float 2.71 with extra 5!
greet(2.71, extra=5)  # Output: Hello, float 2.71 with extra 5!
