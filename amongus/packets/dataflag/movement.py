#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .base import DataFlagPacket
from ...enums import DataFlag
from ...helpers import (
    createVector2,
    pack,
    readVector2,
    unpack,
)


class MovementPacket(DataFlagPacket):
    tag = DataFlag.Network

    @classmethod
    def create(
        cls,
        position: Tuple[int, int],
        velocity: Tuple[int, int],
        sequence_id: int,
    ) -> "MovementPacket":
        return cls(
            b"",
            position=position,
            velocity=velocity,
            sequence_id=sequence_id,
        )

    @classmethod
    def parse(cls, data: bytes) -> "MovementPacket":
        sequence_id = unpack({data[:2]: "h"})
        target_sync_position, _data = readVector2(data[2:])
        target_sync_velocity, _data = readVector2(_data)
        return cls(
            data,
            sequence_id=sequence_id,
            position=target_sync_position,
            velocity=target_sync_velocity,
        )

    def serialize(self, getID: callable) -> bytes:
        return (
            pack({self.values.sequence_id: "h"})
            + createVector2(*self.values.position)
            + createVector2(*self.values.velocity)
        )
