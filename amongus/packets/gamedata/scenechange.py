#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import GameDataPacket
from ...enums import GameDataTag
from ...helpers import createPacked, readPacked, readString, writeString


class SceneChangePacket(GameDataPacket):
    tag = GameDataTag.SceneChangeFlag

    @classmethod
    def create(cls, client_id: int) -> "SceneChangePacket":
        return cls(b"", client_id=client_id)

    @classmethod
    def parse(cls, data: bytes) -> "SceneChangePacket":
        client_id, _data = readPacked(data)
        message, _ = readString(_data)
        return cls(data, client_id=client_id, message=message)

    def serialize(self, getID: callable) -> bytes:
        return (
            bytes([self.tag])
            + createPacked(self.values.client_id)
            + writeString("OnlineGame")
        )
