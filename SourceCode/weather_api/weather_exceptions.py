"""
The module contains custom Warnings and Errors for the OWM Weather API
"""

__all__ = ["ParameterNotSetError", "UnknownLocationError", "OWMConnectionError"]


class ParameterNotSetError(ValueError, AttributeError):
    """
    Exception class to raise if a required parameter is not set.
    """


class UnknownLocationError(ValueError, AttributeError):
    """
    Exception class to raise if a required city or location is not set.
    """


class OWMConnectionError(ConnectionError):
    """
    EXception class to raise if a request to the OpenWEeatherMap api was unsuccessful.
    """
