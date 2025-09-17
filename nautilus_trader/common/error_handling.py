"""
Common error handling utilities for Nautilus Trader.

This module provides reusable error handling patterns and utilities
to improve code consistency and maintainability across the codebase.
"""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar, Union

from nautilus_trader.core.correctness import PyCondition


F = TypeVar("F", bound=Callable[..., Any])


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    log_errors: bool = True,
    logger: Optional[logging.Logger] = None,
    **kwargs,
) -> Any:
    """
    Safely execute a function with error handling.
    
    Parameters
    ----------
    func : Callable
        The function to execute.
    *args
        Positional arguments for the function.
    default_return : Any, optional
        Value to return if function fails.
    log_errors : bool, default True
        Whether to log errors.
    logger : logging.Logger, optional
        Logger to use for error logging.
    **kwargs
        Keyword arguments for the function.
        
    Returns
    -------
    Any
        Function result or default_return on error.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors and logger:
            logger.error(f"Error executing {func.__name__}: {e}")
        return default_return


def validate_not_none(value: Any, name: str) -> Any:
    """
    Validate that a value is not None.
    
    Parameters
    ----------
    value : Any
        The value to validate.
    name : str
        The name of the value for error messages.
        
    Returns
    -------
    Any
        The validated value.
        
    Raises
    ------
    ValueError
        If value is None.
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    return value


def validate_positive(value: Union[int, float], name: str) -> Union[int, float]:
    """
    Validate that a numeric value is positive.
    
    Parameters
    ----------
    value : Union[int, float]
        The value to validate.
    name : str
        The name of the value for error messages.
        
    Returns
    -------
    Union[int, float]
        The validated value.
        
    Raises
    ------
    ValueError
        If value is not positive.
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def retry_on_exception(
    max_retries: int = 3,
    exceptions: tuple = (Exception,),
    delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Callable[[F], F]:
    """
    Decorator to retry function execution on specified exceptions.
    
    Parameters
    ----------
    max_retries : int, default 3
        Maximum number of retry attempts.
    exceptions : tuple, default (Exception,)
        Tuple of exception types to catch and retry on.
    delay : float, default 1.0
        Initial delay between retries in seconds.
    backoff_factor : float, default 2.0
        Factor to multiply delay by after each retry.
        
    Returns
    -------
    Callable
        Decorated function with retry logic.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            # Re-raise the last exception if all retries failed
            raise last_exception
        
        return wrapper
    return decorator


class ErrorContext:
    """
    Context manager for consistent error handling and logging.
    
    Parameters
    ----------
    operation : str
        Description of the operation being performed.
    logger : logging.Logger, optional
        Logger to use for error logging.
    reraise : bool, default True
        Whether to re-raise exceptions after logging.
    """
    
    def __init__(
        self,
        operation: str,
        logger: Optional[logging.Logger] = None,
        reraise: bool = True,
    ):
        self.operation = operation
        self.logger = logger
        self.reraise = reraise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self.logger:
            self.logger.error(f"Error during {self.operation}: {exc_val}")
        
        # Return False to re-raise exception, True to suppress
        return not self.reraise


def ensure_valid_string(value: Any, name: str, min_length: int = 1) -> str:
    """
    Ensure a value is a valid non-empty string.
    
    Parameters
    ----------
    value : Any
        The value to validate.
    name : str
        The name of the value for error messages.
    min_length : int, default 1
        Minimum required string length.
        
    Returns
    -------
    str
        The validated string.
        
    Raises
    ------
    TypeError
        If value is not a string.
    ValueError
        If string is too short.
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string, got {type(value).__name__}")
    
    if len(value) < min_length:
        raise ValueError(f"{name} must be at least {min_length} characters long")
    
    return value


def log_and_raise(
    exception_class: type,
    message: str,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Log an error message and raise an exception.
    
    Parameters
    ----------
    exception_class : type
        The exception class to raise.
    message : str
        The error message.
    logger : logging.Logger, optional
        Logger to use for error logging.
        
    Raises
    ------
    exception_class
        The specified exception with the given message.
    """
    if logger:
        logger.error(message)
    raise exception_class(message)
