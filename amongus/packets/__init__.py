#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This contains all kinds of packets used to serialize and deseralize messages from and
to the server
"""

from .acknowledgement import AcknowledgePacket
from .base import Packet
from .disconnect import DisconnectPacket
from .gamedata import GameDataPacket, MovementPacket, SceneChangePacket
from .hello import HelloPacket
from .matchmaking import (
    AlterGamePacket,
    GetGameListV2Packet,
    JoinGamePacket,
    JoinedGamePacket,
    RedirectPacket,
    ReselectServerPacket,
    StartGamePacket,
)
from .ping import PingPacket
from .reliable import ReliablePacket
from .rpc import (
    CheckColorPacket,
    CheckNamePacket,
    RPCPacket,
    SendChatPacket,
    SetColorPacket,
    SetHatPacket,
    SetNamePacket,
    SetPetPacket,
    SetSkinPacket,
    SetStartCounterPacket,
    SyncSettingsPacket,
    UpdateGameDataPacket,
)
from .spawn import GameDataSpawnPacket, PlayerControlSpawnPacket, SpawnPacket
from .unreliable import UnreliablePacket

__all__ = [
    "Packet",
    "HelloPacket",
    "DisconnectPacket",
    "AcknowledgePacket",
    "PingPacket",
    "ReliablePacket",
    "UnreliablePacket",
    "ReselectServerPacket",
    "JoinGamePacket",
    "RedirectPacket",
    "JoinedGamePacket",
    "GetGameListV2Packet",
    "AlterGamePacket",
    "GameDataPacket",
    "SceneChangePacket",
    "RPCPacket",
    "SetStartCounterPacket",
    "SpawnPacket",
    "PlayerControlSpawnPacket",
    "SendChatPacket",
    "GameDataSpawnPacket",
    "SyncSettingsPacket",
    "UpdateGameDataPacket",
    "StartGamePacket",
    "CheckNamePacket",
    "CheckColorPacket",
    "SetPetPacket",
    "SetHatPacket",
    "SetSkinPacket",
    "SetNamePacket",
    "SetColorPacket",
    "MovementPacket",
]
