#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SetScannerPacket(RPCPacket):
    tag = RPCTag.SetScanner

    @classmethod
    def create(cls, *args, **kwargs) -> "SetScannerPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SetScannerPacket":
        on = bool(data[0])
        count = data[1]
        return cls(data, on=on, count=count)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
