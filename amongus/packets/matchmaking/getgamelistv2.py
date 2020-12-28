#!/usr/bin/python3
# -*- coding: utf-8 -*-
import socket
import struct
from typing import Tuple

from ..base import Packet
from ...enums import GameSettings, MatchMakingTag
from ...game import Game
from ...helpers import (
    createPacked,
    pack,
    readMessage,
    readPacked,
    readString,
    unpack,
)


class GetGameListV2Packet(Packet):
    tag = MatchMakingTag.GetGameListV2

    @classmethod
    def create(
        cls, mapId: GameSettings.Map, impostors: int, language: GameSettings.Keywords
    ) -> "GetGameListV2Packet":
        return cls(b"", mapId=mapId, impostors=impostors, keywords=language)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["GetGameListV2Packet", bytes]:
        _, counts, _data = readMessage(data)
        skeld_count, mirahq_count, polus_count = struct.unpack("III", counts[:12])
        _, _data, _ = readMessage(_data)

        games = []
        while len(_data):
            game = Game()
            _, gamedata, _data = readMessage(_data)
            host, game.port = struct.unpack("Ih", gamedata[:6])
            game.host = ".".join(socket.inet_ntoa(pack({host: "!L"})).split(".")[::-1])
            game.code = unpack({gamedata[6:10]: "I"})
            game.name, _rest = readString(gamedata[10:])
            game.playerCount = _rest[0]
            _age, _rest = readPacked(_rest[1:])
            game.mapId, game.impostors, game.maxPlayers = _rest
            games.append(game)
        return (
            cls(
                data,
                games=games,
                skeld_count=skeld_count,
                mirahq_count=mirahq_count,
                polus_count=polus_count,
            ),
            b"",
        )

    def serialize(self, getID: callable) -> bytes:
        game = Game.with_default_settings()
        # overwrite the defaults with given values
        for key, val in self.values.items():
            if key in ["impostors", "keywords", "mapId"]:
                setattr(game, key, val)
        rest = game.serialize()
        return bytes([self.tag, 0]) + createPacked(len(rest)) + rest
