# type: ignore

import types
import weakref
from abc import get_cache_token
from functools import update_wrapper
from typing import Union, get_args, get_origin, get_type_hints


def _is_union_type(cls):
    return get_origin(cls) in {Union, types.UnionType}


def _is_valid_dispatch_type(cls):
    if isinstance(cls, type):
        return True
    return _is_union_type(cls) and all(isinstance(arg, type) for arg in get_args(cls))


def _find_impl(cls, registry):
    """Find the best matching implementation for a given class."""
    for base in cls.__mro__:
        if base in registry:
            return registry[base]
    return registry.get(object)


def singledispatch(func):
    """Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviors depending upon the type of its first argument. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.
    """
    registry = {}
    dispatch_cache = weakref.WeakKeyDictionary()
    cache_token = None

    def dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to return the best available implementation
        for the given *cls* registered on *generic_func*.
        """
        nonlocal cache_token
        if cache_token is not None:
            current_token = get_cache_token()
            if cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            try:
                impl = registry[cls]
            except KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        return impl

    def register(cls=None, func=None):
        """generic_func.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_func*.
        """
        nonlocal cache_token

        if not isinstance(cls, list):
            clss = [cls]

        if all(_is_valid_dispatch_type(cls) for cls in clss):
            if func is None:
                return lambda f: register(cls, f)
        else:
            if func is not None:
                raise TypeError(
                    f"Invalid first argument to `register()`. "
                    f"{cls!r} is not a class or union type."
                )
            ann = getattr(cls, "__annotations__", {})
            if not ann:
                raise TypeError(
                    f"Invalid first argument to `register()`: {cls!r}. "
                    f"Use either `@register(some_class)` or plain `@register` "
                    f"on an annotated function."
                )
            func = cls

            argname, cls = next(iter(get_type_hints(func).items()))
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

        if _is_union_type(cls):
            for arg in get_args(cls):
                registry[arg] = func
        else:
            registry[cls] = func
        if cache_token is None and hasattr(cls, "__abstractmethods__"):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        return func

    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f"{funcname} requires at least 1 positional argument")
        return dispatch(args[0].__class__)(*args, **kw)

    funcname = getattr(func, "__name__", "singledispatch function")
    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, func)
    return wrapper


# Define a generic function
@singledispatch
def greet(value):
    print(f"Hello, {value}!")


# Register a specific implementation for `int`
@greet.register
def _(value: int):
    print(f"Hello, number {value}!")


# Register a specific implementation for `str`
@greet.register
def _(value: str):
    print(f"Hello, {value.capitalize()}!")


# Register a specific implementation for `list`
@greet.register
def _(value: list):
    print("Hello, everyone!")
    for item in value:
        print(f"- {item}")


# Test the generic function
greet("world")  # Output: Hello, World!
greet(42)  # Output: Hello, number 42!
greet(["Alice", "Bob", "Charlie"])  # Output: Hello, everyone! (and lists names)
greet(3.14)
