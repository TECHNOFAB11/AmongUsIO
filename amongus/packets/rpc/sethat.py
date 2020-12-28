#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SetHatPacket(RPCPacket):
    tag = RPCTag.SetHat

    @classmethod
    def create(cls, hat: int) -> "SetHatPacket":
        return cls(b"", hat=hat)

    @classmethod
    def parse(cls, data: bytes) -> "SetHatPacket":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag, self.values.hat])
