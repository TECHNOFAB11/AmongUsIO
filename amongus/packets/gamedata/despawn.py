#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import GameDataPacket
from ...enums import GameDataTag
from ...helpers import readPacked


class DespawnPacket(GameDataPacket):
    tag = GameDataTag.DespawnFlag

    @classmethod
    def create(cls, *args, **kwargs) -> "DespawnPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "DespawnPacket":
        net_id, _ = readPacked(data)
        return cls(data, net_id=net_id)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
