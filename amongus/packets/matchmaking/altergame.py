#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple
from ...enums import MatchMakingTag
from ...helpers import unpack
from ...packets import Packet


class AlterGamePacket(Packet):
    tag = MatchMakingTag.AlterGame

    @classmethod
    def create(cls, *args, **kwargs) -> "AlterGamePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["AlterGamePacket", bytes]:
        game_code = unpack({data[0:4]: "I"})
        return cls(data, game_code=game_code, public=bool(data[5])), b""

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
