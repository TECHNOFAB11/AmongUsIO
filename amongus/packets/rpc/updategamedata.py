#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import unpack
from ...player import Player


class UpdateGameDataPacket(RPCPacket):
    tag = RPCTag.UpdateGameData

    @classmethod
    def create(cls, *args, **kwargs) -> "UpdateGameDataPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "UpdateGameDataPacket":
        _data = data
        players = []
        while len(_data) > 0:
            size = unpack({_data[:2]: "h"})
            p, _data = Player.deserialize(_data[2 : size + 3])
            players.append(p)
        return cls(data, players=players)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
