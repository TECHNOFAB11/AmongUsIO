#!/usr/bin/python3
# -*- coding: utf-8 -*-


class AmongUsException(Exception):
    """Base Exception from which all exceptions of this package derive"""

    pass


class ConnectionException(AmongUsException):
    """
    Exception which gets raised when something went wrong with the connection

    Attributes:
        message (str): Message which explains more about the error
        reason (int): A DisconnectReason to be able to programmatically
            check what went wrong
        custom_reason (str): If reason is :attr:`DisconnectReason.Custom`, this will
            contain the custom disconnect reason sent by the Among Us server
    """

    custom_reason: str

    def __init__(self, message: str, reason: int, **kwargs):
        """
        Initializes the exception and sets the passed kwargs as attributes

        Args:
            message (str): The message for the user
            reason (int): The :class:`DisconnectReason` why the connection was closed
        """
        self.reason = reason
        self.message = message
        for key, val in kwargs.items():
            setattr(self, key, val)
        super().__init__(self.message)
