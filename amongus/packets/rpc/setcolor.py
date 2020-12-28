#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SetColorPacket(RPCPacket):
    tag = RPCTag.SetColor

    @classmethod
    def create(cls, *args, **kwargs) -> "SetColorPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SetColorPacket":
        return cls(data, color=data[0])

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
