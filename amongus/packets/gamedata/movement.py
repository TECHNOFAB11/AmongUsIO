#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .base import GameDataPacket
from ...enums import GameDataTag
from ...helpers import (
    createPacked,
    createVector2,
    pack,
    readPacked,
    readVector2,
    unpack,
)


class MovementPacket(GameDataPacket):
    tag = GameDataTag.DataFlag

    @classmethod
    def create(
        cls,
        position: Tuple[int, int],
        velocity: Tuple[int, int],
        net_id: int,
        sequence_id: int,
    ) -> "MovementPacket":
        return cls(
            b"",
            position=position,
            velocity=velocity,
            net_id=net_id,
            sequence_id=sequence_id,
        )

    @classmethod
    def parse(cls, data: bytes) -> "MovementPacket":
        net_id, _data = readPacked(data)
        sequence_id = unpack({_data[:2]: "h"})
        target_sync_position, _data = readVector2(_data[2:])
        target_sync_velocity, _data = readVector2(_data)
        return cls(
            data,
            net_id=net_id,
            sequence_id=sequence_id,
            position=target_sync_position,
            velocity=target_sync_velocity,
        )

    def serialize(self, getID: callable) -> bytes:
        return (
            bytes([self.tag])
            + createPacked(self.values.net_id)
            + pack({self.values.sequence_id: "h"})
            + createVector2(*self.values.position)
            + createVector2(*self.values.velocity)
        )
