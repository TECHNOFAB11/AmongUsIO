#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import GameDataPacket
from ...enums import GameDataTag
from ...helpers import pack


class SceneChangePacket(GameDataPacket):
    tag = GameDataTag.SceneChangeFlag

    @classmethod
    def create(cls, client_id: int) -> "SceneChangePacket":
        return cls(b"", client_id=client_id)

    @classmethod
    def parse(cls, data: bytes) -> "SceneChangePacket":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + pack({self.values.client_id: "I"}) + b"OnlineGame"
