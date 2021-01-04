#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class ClosePacket(RPCPacket):
    tag = RPCTag.Close

    @classmethod
    def create(cls, *args, **kwargs) -> "ClosePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "ClosePacket":
        return cls(data)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
