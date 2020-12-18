#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import SpawnPacket
from ...enums import SpawnTag
from ...helpers import readPacked, readMessage


class PlayerControlSpawnPacket(SpawnPacket):
    tag = SpawnTag.PlayerControl

    @classmethod
    def create(cls, *args, **kwargs) -> "PlayerControlSpawnPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "PlayerControlSpawnPacket":
        net_id, _data = readPacked(data)
        _, controldata, _ = readMessage(_data)
        player_id = controldata[1]
        return cls(data, net_id=net_id, player_id=player_id)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
