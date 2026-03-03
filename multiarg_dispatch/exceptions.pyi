"""Type stubs for multiarg-dispatch exceptions."""

class MultiArgDispatchError(Exception):
    """Base exception for all multiarg-dispatch errors."""

    ...

class MissingTypeAnnotationError(MultiArgDispatchError, TypeError):
    """Raised when a function parameter lacks a required type annotation."""

    ...

class InvalidTypeAnnotationError(MultiArgDispatchError, TypeError):
    """Raised when a type annotation is not valid for dispatch."""

    ...

class RegistrationError(MultiArgDispatchError, TypeError):
    """Raised when function registration fails."""

    ...

class NoMatchingImplementationError(MultiArgDispatchError, TypeError):
    """Raised when no matching implementation is found for given argument types."""

    ...
