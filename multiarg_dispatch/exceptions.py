"""Custom exceptions for multiarg-dispatch."""


class MultiArgDispatchError(Exception):
    """Base exception for all multiarg-dispatch errors."""

    pass


class MissingTypeAnnotationError(MultiArgDispatchError, TypeError):
    """Raised when a function parameter lacks a required type annotation."""

    pass


class InvalidTypeAnnotationError(MultiArgDispatchError, TypeError):
    """Raised when a type annotation is not valid for dispatch.

    Valid dispatch types are:
    - Regular classes (type objects)
    - Union types where all members are classes
    """

    pass


class RegistrationError(MultiArgDispatchError, TypeError):
    """Raised when function registration fails.

    This typically occurs when registering a function with a different
    number of parameters than the base function.
    """

    pass
