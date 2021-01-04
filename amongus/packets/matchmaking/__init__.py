#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""All :class:`MatchMakingTag` packets."""

from .altergame import AlterGamePacket
from .endgame import EndGamePacket
from .getgamelistv2 import GetGameListV2Packet
from .joinedgame import JoinedGamePacket
from .joingame import JoinGamePacket
from .redirect import RedirectPacket
from .removeplayer import RemovePlayerPacket
from .reselectserver import ReselectServerPacket
from .startgame import StartGamePacket

__all__ = [
    "ReselectServerPacket",
    "JoinGamePacket",
    "RedirectPacket",
    "JoinedGamePacket",
    "GetGameListV2Packet",
    "AlterGamePacket",
    "StartGamePacket",
    "EndGamePacket",
    "RemovePlayerPacket",
]
