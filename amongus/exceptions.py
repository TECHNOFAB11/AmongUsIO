#!/usr/bin/python3
# -*- coding: utf-8 -*-


class AmongUsException(Exception):
    pass


class ConnectionException(AmongUsException):
    custom_reason: str

    def __init__(self, message: str, reason: int, **kwargs):
        self.reason = reason
        self.message = message
        for key, val in kwargs.items():
            setattr(self, key, val)
        super().__init__(self.message)
