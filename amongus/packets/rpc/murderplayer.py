#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readPacked


class MurderPlayerPacket(RPCPacket):
    tag = RPCTag.MurderPlayer

    @classmethod
    def create(cls, *args, **kwargs) -> "MurderPlayerPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "MurderPlayerPacket":
        target, _ = readPacked(data)
        return cls(data, target=target)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
