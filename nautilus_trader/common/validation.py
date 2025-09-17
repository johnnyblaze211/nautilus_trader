"""
Common validation utilities for Nautilus Trader.

This module provides reusable validation functions to improve code
consistency and reduce duplication across the codebase.
"""

from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

from nautilus_trader.core.correctness import PyCondition


def validate_config_dict(
    config: Dict[str, Any],
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None,
) -> None:
    """
    Validate configuration dictionary has required keys.
    
    Parameters
    ----------
    config : Dict[str, Any]
        Configuration dictionary to validate.
    required_keys : List[str]
        List of required keys.
    optional_keys : List[str], optional
        List of optional keys.
        
    Raises
    ------
    ValueError
        If required keys are missing or unknown keys are present.
    """
    PyCondition.not_none(config, "config")
    PyCondition.not_empty(required_keys, "required_keys")
    
    # Check for missing required keys
    missing_keys = set(required_keys) - set(config.keys())
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    # Check for unknown keys if optional_keys is provided
    if optional_keys is not None:
        allowed_keys = set(required_keys) | set(optional_keys)
        unknown_keys = set(config.keys()) - allowed_keys
        if unknown_keys:
            raise ValueError(f"Unknown configuration keys: {unknown_keys}")


def validate_price_precision(price: Union[float, Decimal], precision: int) -> None:
    """
    Validate price has correct precision.
    
    Parameters
    ----------
    price : Union[float, Decimal]
        Price to validate.
    precision : int
        Required decimal precision.
        
    Raises
    ------
    ValueError
        If price precision is invalid.
    """
    PyCondition.not_none(price, "price")
    PyCondition.not_negative_int(precision, "precision")
    
    if isinstance(price, float):
        price_str = f"{price:.{precision + 2}f}"
    else:
        price_str = str(price)
    
    decimal_places = len(price_str.split('.')[-1]) if '.' in price_str else 0
    
    if decimal_places > precision:
        raise ValueError(
            f"Price {price} has {decimal_places} decimal places, "
            f"maximum allowed is {precision}"
        )


def validate_quantity_precision(quantity: Union[float, Decimal], precision: int) -> None:
    """
    Validate quantity has correct precision.
    
    Parameters
    ----------
    quantity : Union[float, Decimal]
        Quantity to validate.
    precision : int
        Required decimal precision.
        
    Raises
    ------
    ValueError
        If quantity precision is invalid.
    """
    PyCondition.not_none(quantity, "quantity")
    PyCondition.not_negative_int(precision, "precision")
    
    if isinstance(quantity, float):
        quantity_str = f"{quantity:.{precision + 2}f}"
    else:
        quantity_str = str(quantity)
    
    decimal_places = len(quantity_str.split('.')[-1]) if '.' in quantity_str else 0
    
    if decimal_places > precision:
        raise ValueError(
            f"Quantity {quantity} has {decimal_places} decimal places, "
            f"maximum allowed is {precision}"
        )


def validate_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    name: str = "value",
) -> None:
    """
    Validate value is within specified range.
    
    Parameters
    ----------
    value : Union[int, float]
        Value to validate.
    min_value : Union[int, float], optional
        Minimum allowed value (inclusive).
    max_value : Union[int, float], optional
        Maximum allowed value (inclusive).
    name : str, default "value"
        Name of the value for error messages.
        
    Raises
    ------
    ValueError
        If value is outside the specified range.
    """
    PyCondition.not_none(value, name)
    
    if min_value is not None and value < min_value:
        raise ValueError(f"{name} {value} is below minimum {min_value}")
    
    if max_value is not None and value > max_value:
        raise ValueError(f"{name} {value} is above maximum {max_value}")


def validate_string_in_choices(
    value: str,
    choices: List[str],
    name: str = "value",
    case_sensitive: bool = True,
) -> str:
    """
    Validate string is one of the allowed choices.
    
    Parameters
    ----------
    value : str
        String to validate.
    choices : List[str]
        List of allowed choices.
    name : str, default "value"
        Name of the value for error messages.
    case_sensitive : bool, default True
        Whether comparison should be case sensitive.
        
    Returns
    -------
    str
        The validated string (potentially normalized if case_sensitive=False).
        
    Raises
    ------
    ValueError
        If value is not in choices.
    """
    PyCondition.not_none(value, name)
    PyCondition.not_empty(choices, "choices")
    
    if case_sensitive:
        if value not in choices:
            raise ValueError(f"{name} '{value}' must be one of {choices}")
        return value
    else:
        value_lower = value.lower()
        choices_lower = [choice.lower() for choice in choices]
        
        if value_lower not in choices_lower:
            raise ValueError(f"{name} '{value}' must be one of {choices}")
        
        # Return the original case from choices
        index = choices_lower.index(value_lower)
        return choices[index]


def validate_list_not_empty(value: List[Any], name: str = "list") -> None:
    """
    Validate list is not empty.
    
    Parameters
    ----------
    value : List[Any]
        List to validate.
    name : str, default "list"
        Name of the list for error messages.
        
    Raises
    ------
    ValueError
        If list is empty.
    """
    PyCondition.not_none(value, name)
    
    if not value:
        raise ValueError(f"{name} cannot be empty")


def validate_dict_not_empty(value: Dict[Any, Any], name: str = "dict") -> None:
    """
    Validate dictionary is not empty.
    
    Parameters
    ----------
    value : Dict[Any, Any]
        Dictionary to validate.
    name : str, default "dict"
        Name of the dictionary for error messages.
        
    Raises
    ------
    ValueError
        If dictionary is empty.
    """
    PyCondition.not_none(value, name)
    
    if not value:
        raise ValueError(f"{name} cannot be empty")


def validate_percentage(value: Union[int, float], name: str = "percentage") -> None:
    """
    Validate value is a valid percentage (0-100).
    
    Parameters
    ----------
    value : Union[int, float]
        Percentage value to validate.
    name : str, default "percentage"
        Name of the value for error messages.
        
    Raises
    ------
    ValueError
        If value is not between 0 and 100.
    """
    validate_range(value, min_value=0, max_value=100, name=name)


def validate_url(url: str, name: str = "url") -> None:
    """
    Validate URL format.
    
    Parameters
    ----------
    url : str
        URL to validate.
    name : str, default "url"
        Name of the URL for error messages.
        
    Raises
    ------
    ValueError
        If URL format is invalid.
    """
    PyCondition.not_none(url, name)
    
    if not isinstance(url, str):
        raise ValueError(f"{name} must be a string")
    
    if not url.strip():
        raise ValueError(f"{name} cannot be empty")
    
    # Basic URL validation
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("ws://") or url.startswith("wss://")):
        raise ValueError(f"{name} must start with http://, https://, ws://, or wss://")
