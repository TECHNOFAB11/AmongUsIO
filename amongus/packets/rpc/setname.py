#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readString


class SetNamePacket(RPCPacket):
    tag = RPCTag.SetName

    @classmethod
    def create(cls, *args, **kwargs) -> "SetNamePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SetNamePacket":
        name, _ = readString(data)
        return cls(data, name=name)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
