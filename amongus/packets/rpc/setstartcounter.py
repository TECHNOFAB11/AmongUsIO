#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readPacked


class SetStartCounterPacket(RPCPacket):
    tag = RPCTag.SetStartCounter

    @classmethod
    def create(cls, *args, **kwargs) -> "SetStartCounterPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SetStartCounterPacket":
        counter, _data = readPacked(data)
        secondsleft = _data[0]
        return cls(data, counter=counter, secondsleft=secondsleft)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
