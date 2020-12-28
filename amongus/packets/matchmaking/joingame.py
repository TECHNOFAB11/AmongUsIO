#!/usr/bin/python3
# -*- coding: utf-8 -*-
import struct
from typing import Tuple

from ..base import Packet
from ...enums import DisconnectReason, MatchMakingTag
from ...helpers import gameNameToInt, pack, unpack


class JoinGamePacket(Packet):
    tag = MatchMakingTag.JoinGame

    @classmethod
    def create(cls, lobby_code: str) -> "JoinGamePacket":
        return cls(b"", lobby_code=lobby_code)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["JoinGamePacket", bytes]:
        reason = unpack({data[:4]: "I"})
        if DisconnectReason.has_value(reason):
            custom_reason = None
            if reason == DisconnectReason.Custom:
                size = data[4]
                custom_reason = data[5 : 5 + size].decode()
            return cls(data, reason=reason, custom_reason=custom_reason), b""
        else:
            game_code, player_id, host_id = struct.unpack("III", data[:12])
            return (
                cls(
                    data[:12], game_code=game_code, player_id=player_id, host_id=host_id
                ),
                data[12:],
            )

    def serialize(self, getID: callable) -> bytes:
        return (
            bytes([self.tag])
            + pack({gameNameToInt(self.values.lobby_code): "I"})
            + bytes([0x7])
        )
