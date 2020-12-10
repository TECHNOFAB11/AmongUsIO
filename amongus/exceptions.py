#!/usr/bin/python3
# -*- coding: utf-8 -*-


class AmongUsException(Exception):
    pass


class ConnectionError(AmongUsException):
    custom_reason: str

    def __init__(self, reason, message: str, **kwargs):
        self.reason = reason
        self.message = message
        [setattr(self, key, val) for key, val in kwargs.items()]
        super().__init__(self.message)
