#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This contains all kinds of packets used to serialize and deseralize messages from and
to the server
"""

from .acknowledgement import AcknowledgePacket
from .base import Packet
from .dataflag import DataFlagPacket, MovementPacket
from .disconnect import DisconnectPacket
from .gamedata import DespawnPacket, GameDataPacket, ReadyPacket, SceneChangePacket
from .hello import HelloPacket
from .matchmaking import (
    AlterGamePacket,
    EndGamePacket,
    GetGameListV2Packet,
    JoinGamePacket,
    JoinedGamePacket,
    RedirectPacket,
    RemovePlayerPacket,
    ReselectServerPacket,
    StartGamePacket,
)
from .ping import PingPacket
from .reliable import ReliablePacket
from .rpc import (
    CheckColorPacket,
    CheckNamePacket,
    ClosePacket,
    MurderPlayerPacket,
    RPCPacket,
    ReportDeadBodyPacket,
    SendChatNotePacket,
    SendChatPacket,
    SetColorPacket,
    SetHatPacket,
    SetInfectedPacket,
    SetNamePacket,
    SetPetPacket,
    SetSkinPacket,
    SetStartCounterPacket,
    SetTasksPacket,
    SnapToPacket,
    StartMeetingPacket,
    SyncSettingsPacket,
    UpdateGameDataPacket,
    VotingCompletePacket,
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
    "DataFlagPacket",
    "DespawnPacket",
    "ReadyPacket",
    "SetInfectedPacket",
    "SetTasksPacket",
    "MurderPlayerPacket",
    "ReportDeadBodyPacket",
    "StartMeetingPacket",
    "VotingCompletePacket",
    "ClosePacket",
    "SnapToPacket",
    "SendChatNotePacket",
    "MovementPacket",
    "EndGamePacket",
    "RemovePlayerPacket",
]
