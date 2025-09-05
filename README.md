# multidispatch

Package for replacing singledispatch of functools where it looks at all function inputs instead of just the first one.

# Changes compared to singledispatch

Multidispatch is basically singledispatches code only altered to suit multiple type hints instead of just the first arguments, below are the changes made to the singledispatch code:

- Updated _find_impl to handle a tuple as input for cls and match it accordingly in the registry.
- Updated _find_impl to handle union_types instead of within the register function. 
- Updated the wrapper to now pass all the type hints including the ones in the kwargs.
- Updated register to save not just the type of the first argument but instead save the types of all the arguments as tuple in the key of the registry.
- dispatch_cache for efficiency is removed because the registery now always contains tuples as keys and these do not support weak references (only user defined types do).
- The check on the cache token is also removed since it is obsolete after removing the dispatch cache.
- The option to pass the type hint as an argument in register is removed, multidispatch only looks at the type hints given.
- Added an error that gets thrown when there are arguments passed without type hints in the register.
- Added an error when the number of arguments does not match the original number of arguments.
- Added a warning for when a value has a default since these are not considered in dispatching when the function is called.