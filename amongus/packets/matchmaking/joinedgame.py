#!/usr/bin/python3
# -*- coding: utf-8 -*-
import struct
from typing import Tuple
from ...enums import MatchMakingTag
from ...helpers import readPacked
from ...packets import Packet


class JoinedGamePacket(Packet):
    tag = MatchMakingTag.JoinedGame

    @classmethod
    def create(cls, *args, **kwargs) -> "JoinedGamePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["JoinedGamePacket", bytes]:
        game_id, client_id, host_id = struct.unpack("III", data[:12])
        player_amount, _data = readPacked(data[12:])
        player_ids = []
        while len(_data) > 0:
            _id, _data = readPacked(_data)
            player_ids.append(_id)
        return (
            cls(
                data,
                game_id=game_id,
                client_id=client_id,
                host_id=host_id,
                player_amount=player_amount,
                player_ids=player_ids,
            ),
            b"",
        )

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
