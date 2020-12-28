#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class CheckColorPacket(RPCPacket):
    tag = RPCTag.CheckColor

    @classmethod
    def create(cls, color: int) -> "CheckColorPacket":
        return cls(b"", color=color)

    @classmethod
    def parse(cls, data: bytes) -> "CheckColorPacket":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag, self.values.color])
