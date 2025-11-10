# type: ignore

import inspect
import types
import warnings
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
        # Skip the default implementation
        if registered_types is object:
            continue
        match = True
        # Check each argument type against the registered types
        for arg, reg in zip(arg_types, registered_types):
            # Handle Union types in the registry
            if _is_union_type(reg):
                if not any(issubclass(arg, r) for r in get_args(reg)):
                    match = False
            # Handle regular types
            if not issubclass(arg, reg):
                match = False
        if match:
            return func
    return registry.get(object)


def multidispatch(func):
    """Multi-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviors depending upon the type of its arguments. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.
    """
    registry = {}
    # Save default number of arguments for validation during registration
    n_arguments = len(inspect.signature(func).parameters)

    def dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to return the best available implementation
        for the given *cls* registered on *generic_func*.
        """
        try:
            impl = registry[cls]
        except KeyError:
            impl = _find_impl(cls, registry)
        return impl

    def register(func=None):
        """generic_func.register(func) -> func

        Registers a new implementation for the given *cls* on a *generic_func*.
        """

        # Extract type hints
        type_hints = get_type_hints(func)
        arg_type_hints = {k: v for k, v in type_hints.items() if k != "return"}
        # Validate type hints to make sure all arguments are annotated
        sig = inspect.signature(func)
        if len(arg_type_hints) != len(sig.parameters):
            raise TypeError(
                f"All arguments must be type-annotated for {funcname!r}. "
                f"Got {len(arg_type_hints)} annotations for {len(sig.parameters)} parameters."
            )
        # Warn if any parameters have default values
        for name, param in sig.parameters.items():
            if param.default is not inspect._empty:
                warnings.warn(
                    f"Parameter '{name}' has a default value ({param.default}).\n "
                    f"Note that default values are not considered in dispatching when calling the function.",
                    category=DispatchWarning,
                )
        # Validate that all type hints are valid dispatch types
        for argname, cls in arg_type_hints.items():
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

        clss = [cls for _, cls in arg_type_hints.items()]

        if n_arguments != len(clss):
            raise TypeError(
                f"Cannot register {func!r} for types {clss}. "
                f"Expected {n_arguments} types."
            )

        registry[tuple(clss)] = func

        return func

    def wrapper(*args, **kw):
        if not args and not kw:
            raise TypeError(f"{funcname} requires at least 1 argument")
        cls_args = [arg.__class__ for arg in args]

        if kw is not None:
            cls_kw = [type(value) for value in kw.values()]
            cls_args.extend(cls_kw)

        return dispatch(tuple(cls_args))(*args, **kw)

    funcname = getattr(func, "__name__", "multidispatch function")
    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    update_wrapper(wrapper, func)
    return wrapper
