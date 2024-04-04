"""
The module contains custom Warnings and Errors for the Camer Interface
"""

__all__ = ["ParameterNotSetError", "BadCameraInterface"]


class ParameterNotSetError(ValueError, AttributeError):
    """
    Exception class to raise if a required parameter is not set.
    """


class BadCameraInterface(Exception):
    """
    Exception class to raise if a request to the camera interface was unsuccessful.
    """


class BadVideoFile(Exception):
    """
    Exception class to raise if a request to the file was unsuccessful.
    """
