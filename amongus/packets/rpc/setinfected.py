#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SetInfectedPacket(RPCPacket):
    tag = RPCTag.SetInfected

    @classmethod
    def create(cls, *args, **kwargs) -> "SetInfectedPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SetInfectedPacket":
        _data = bytearray(data)
        host = _data[0]
        impostor_ids = []
        for _id in _data[1:]:
            impostor_ids.append(_id)
        return cls(data, host=host, impostor_ids=impostor_ids)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
