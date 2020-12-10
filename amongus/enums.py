#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import IntEnum


class AmongUsEnum(IntEnum):
    pass


class PacketType(AmongUsEnum):
    Unreliable = 0
    Reliable = 1
    Hello = 8
    Disconnect = 9
    Acknowledgement = 10
    Fragment = 11
    Ping = 12


class MatchMakingTag(AmongUsEnum):
    HostGame = 0
    JoinGame = 1
    StartGame = 2
    RemoveGame = 3
    RemovePlayer = 4
    GameData = 5
    GameDataTo = 6
    JoinedGame = 7
    EndGame = 8
    AlterGame = 10
    KickPlayer = 11
    WaitForHost = 12
    Redirect = 13
    ReselectServer = 14
    GetGameList = 9
    GetGameListV2 = 16


class DisconnectReason(AmongUsEnum):
    ExitGame = 0
    GameFull = 1
    GameStarted = 2
    GameNotFound = 3
    IncorrectVersion = 5
    Banned = 6
    Kicked = 7
    Custom = 8
    InvalidName = 9
    Hacking = 10
    Destroy = 16
    Error = 17
    IncorrectGame = 18
    ServerRequest = 19
    ServerFull = 20
    FocusLostBackground = 207
    IntentionalLeaving = 208
    FocusLost = 209
    NewConnection = 210

    # Internal reasons from this package
    Timeout = 1000
    UnansweredPings = 1001
