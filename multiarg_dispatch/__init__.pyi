"""Type stubs for multiarg-dispatch package."""

from .exceptions import (
    InvalidTypeAnnotationError as InvalidTypeAnnotationError,
)
from .exceptions import (
    MissingTypeAnnotationError as MissingTypeAnnotationError,
)
from .exceptions import (
    MultiArgDispatchError as MultiArgDispatchError,
)
from .exceptions import (
    NoMatchingImplementationError as NoMatchingImplementationError,
)
from .exceptions import (
    RegistrationError as RegistrationError,
)
from .main import DispatchWarning as DispatchWarning
from .main import multidispatch as multidispatch

__all__ = [
    "multidispatch",
    "DispatchWarning",
    "MultiArgDispatchError",
    "MissingTypeAnnotationError",
    "InvalidTypeAnnotationError",
    "RegistrationError",
    "NoMatchingImplementationError",
]
