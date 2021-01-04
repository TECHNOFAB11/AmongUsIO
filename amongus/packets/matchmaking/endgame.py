#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from ...enums import GameOverReason, MatchMakingTag
from ...helpers import unpack
from ...packets import Packet


class EndGamePacket(Packet):
    tag = MatchMakingTag.EndGame

    @classmethod
    def create(cls, *args, **kwargs) -> "EndGamePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["EndGamePacket", bytes]:
        game_id = unpack({data[:4]: "I"})
        reason = data[5]
        if GameOverReason.has_value(reason):
            reason = GameOverReason(reason)
        return cls(data, game_id=game_id, reason=reason), b""

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
