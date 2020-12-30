#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import SpawnPacket
from ...enums import SpawnTag
from ...helpers import dotdict, readMessage, readPacked


class PlayerControlSpawnPacket(SpawnPacket):
    tag = SpawnTag.PlayerControl

    @classmethod
    def create(cls, *args, **kwargs) -> "PlayerControlSpawnPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "PlayerControlSpawnPacket":
        net_ids = dotdict()

        net_ids["control"], _data = readPacked(data)
        _, control_data, _data = readMessage(_data)
        net_ids["physics"], _data = readPacked(_data)
        _, physics_data, _data = readMessage(_data)
        net_ids["network"], _data = readPacked(_data)
        _, network_data, _data = readMessage(_data)
        player_id = control_data[1]
        return cls(data, player_id=player_id, net_ids=net_ids)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
