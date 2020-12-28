#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import createPacked


class CheckNamePacket(RPCPacket):
    tag = RPCTag.CheckName

    @classmethod
    def create(cls, name: str) -> "CheckNamePacket":
        return cls(b"", name=name)

    @classmethod
    def parse(cls, data: bytes) -> "CheckNamePacket":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        rest = self.values.name.encode()
        return bytes([self.tag]) + createPacked(len(rest)) + rest
