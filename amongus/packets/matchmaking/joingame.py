#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple
from ..base import Packet
from ...enums import MatchMakingTag, DisconnectReason
from ...helpers import unpack, pack

alphabet = "QWXRTYLPESDFGHUJKZOCVBINMA"
char_map: dict = {
    chr(x): list(alphabet).index(chr(x)) for x in range(ord("A"), ord("Z") + 1)
}


def gameNameToInt(game_name: str):
    (a, b, c, d, e, f) = (char_map[char] for char in game_name.upper())
    return (
        (a + 26 * b) & 0x3FF
        | ((c + 26 * (d + 26 * (e + 26 * f))) << 10) & 0x3FFFFC00
        | 0x80000000
    )


class JoinGamePacket(Packet):
    tag = MatchMakingTag.JoinGame

    @classmethod
    def create(cls, lobby_code: str) -> "JoinGamePacket":
        return cls(b"", lobby_code=lobby_code)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["JoinGamePacket", bytes]:
        reason = unpack({data[:4]: "I"})
        custom_reason = None
        if reason == DisconnectReason.Custom:
            size = data[4]
            custom_reason = data[5 : 5 + size].decode()
        return cls(data, reason=reason, custom_reason=custom_reason), b""

    def serialize(self, getID: callable) -> bytes:
        return (
            bytes([self.tag])
            + pack({gameNameToInt(self.values.lobby_code): "I"})
            + bytes([0x7])
        )
