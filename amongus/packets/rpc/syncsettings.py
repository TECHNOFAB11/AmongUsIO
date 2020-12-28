#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...game import Game
from ...helpers import readPacked


class SyncSettingsPacket(RPCPacket):
    tag = RPCTag.SyncSettings

    @classmethod
    def create(cls, *args, **kwargs) -> "SyncSettingsPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SyncSettingsPacket":
        size, _data = readPacked(data)
        game = Game.deserialize(_data[:size])
        return cls(data, game=game)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
