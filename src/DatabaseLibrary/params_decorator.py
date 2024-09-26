"""
These decorators are introduced for the transition from old argument naming / positioning to the new one.
"""
from functools import wraps
from inspect import signature

from robot.api import logger


def renamed_args(mapping):
    """
    Decorator to rename arguments and warn users about deprecated argument names.

    :param mapping: Dictionary mapping old argument names to new argument names.
    :return: The decorated function with remapped arguments.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if any old argument names are used
            for old_name, new_name in mapping.items():
                if old_name in kwargs:
                    # Issue a warning to the user
                    logger.warn(f"Argument '{old_name}' is deprecated, use '{new_name}' instead")
                    # Move the argument value to the new name
                    logger.info(f"Replacing '{old_name}' with '{new_name}'")
                    kwargs[new_name] = kwargs.pop(old_name)
            # Call the original function with updated kwargs
            return func(*args, **kwargs)

        return wrapper

    return decorator


def deprecated_positional_args(allowed_pos_args_count):
    """
    Warn about using too many positional arguments
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)

            # Issue a warning if not allowed positional arguments are used
            if len(bound_args.args) > allowed_pos_args_count + 1:
                logger.warn(
                    f"Using more than {allowed_pos_args_count} positional arguments in this keyword "
                    "is deprecated, use named arguments instead"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
