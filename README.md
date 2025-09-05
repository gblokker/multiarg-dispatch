# multiarg-dispatch

`multiarg-dispatch` is a Python package that extends the functionality of `functools.singledispatch` to allow dispatching based on **type hints for all arguments**, not just the first one. It provides a simple decorator to define generic functions with multiple implementations depending on argument types.

## Features

- Dispatch functions based on the types of **all arguments**, including keyword arguments.
- Supports **union types** in type hints.
- Raises a warning if arguments have default values (since defaults are not considered during dispatch).
- Type checking enforced at registration: all parameters must have type hints.
- Fully compatible with Python 3.13+.

## Installation

Install via Poetry (or include in your project):

```bash
poetry add multiarg-dispatch
````

Or via pip:

```bash
pip install multiarg-dispatch
```

Or clone and install manually:

```bash
git clone <repo-url>
cd multiarg-dispatch
poetry install
```

## Usage

```python
from multiarg_dispatch import multidispatch, DispatchWarning

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

print(test_func(10))            # int:10,str:default
print(test_func("hello", []))   # str:hello,list:[]
print(test_func(3.14, "extra")) # float:3.14,union:extra
```

## API

### `multidispatch(func)`

Decorator to make a function multi-dispatch capable.

* `register(func)`: Register a new implementation based on type hints.
* `dispatch(cls)`: Retrieve the implementation for given types.
* `registry`: Read-only view of all registered implementations.

### `DispatchWarning`

Warning raised when dispatching might be affected by defaults.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Make your changes.
4. Ensure all tests pass (`pytest` recommended).
5. Open a Pull Request with a clear description of your changes.

Please follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines and include type hints where appropriate.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

