#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import GameDataPacket
from ...enums import GameDataTag
from ...helpers import createPacked, readPacked


class ReadyPacket(GameDataPacket):
    tag = GameDataTag.ReadyFlag

    @classmethod
    def create(cls, client_id: int) -> "ReadyPacket":
        return cls(b"", client_id=client_id)

    @classmethod
    def parse(cls, data: bytes) -> "ReadyPacket":
        client_id, _ = readPacked(data)
        return cls(data, client_id=client_id)

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + createPacked(self.values.client_id)
