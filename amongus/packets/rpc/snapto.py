#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import createVector2, readVector2


class SnapToPacket(RPCPacket):
    tag = RPCTag.SnapTo

    @classmethod
    def create(cls, position: Tuple[int, int], sequence_id) -> "SnapToPacket":
        return cls(b"", position=position, sequence_id=sequence_id)

    @classmethod
    def parse(cls, data: bytes) -> "SnapToPacket":
        position, _data = readVector2(data)
        sequence_id = _data[0]
        return cls(data, position=position, sequence_id=sequence_id)

    def serialize(self, getID: callable) -> bytes:
        return (
            bytes([self.tag])
            + createVector2(*self.values.position)
            + bytes([self.values.sequence_id])
        )
