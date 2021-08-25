"""This module contains custom errors. Reason why I have them defined:
Easier stopping and logging in the event of failure."""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass




class NotSupportedFormatError(Error):
    """ Raised when an input file has a not supported extension.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

