#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SetSkinPacket(RPCPacket):
    tag = RPCTag.SetSkin

    @classmethod
    def create(cls, skin: int) -> "SetSkinPacket":
        return cls(b"", skin=skin)

    @classmethod
    def parse(cls, data: bytes) -> "SetSkinPacket":
        return cls(data, skin=data[0])

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag, self.values.skin])
