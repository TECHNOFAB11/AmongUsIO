#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from ..base import Packet
from ...enums import MatchMakingTag
from ...helpers import pack, unpack


class StartGamePacket(Packet):
    tag = MatchMakingTag.StartGame

    @classmethod
    def create(cls, game_id: int) -> "StartGamePacket":
        return cls(b"", game_id=game_id)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["StartGamePacket", bytes]:
        game_id = unpack({data[:4]: "I"})
        return cls(data, game_id=game_id), b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + pack({self.values.game_id: "I"})
