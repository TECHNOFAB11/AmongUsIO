#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import SpawnPacket
from ...enums import SpawnTag
from ...helpers import readMessage, readPacked
from ...player import Player


class GameDataSpawnPacket(SpawnPacket):
    tag = SpawnTag.GameData

    @classmethod
    def create(cls, *args, **kwargs) -> "GameDataSpawnPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "GameDataSpawnPacket":
        net_id, _data = readPacked(data)
        _, gamedata, _ = readMessage(_data)
        num_players, _data = readPacked(gamedata)
        players = []
        for _ in range(num_players):
            p, _data = Player.deserialize(_data)
            players.append(p)
        return cls(data, net_id=net_id, num_players=num_players, players=players)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
