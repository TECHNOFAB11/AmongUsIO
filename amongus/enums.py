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


class AlterGameTag(AmongUsEnum):
    ChangePrivacy = 1


class GameDataTag(AmongUsEnum):
    DataFlag = 1
    RpcFlag = 2
    SpawnFlag = 4
    DespawnFlag = 5
    SceneChangeFlag = 6
    ReadyFlag = 7
    ChangeSettingsFlag = 8


class RPCTag(AmongUsEnum):
    PlayAnimation = 0
    CompleteTask = 1
    SyncSettings = 2
    SetInfected = 3
    Exiled = 4
    CheckName = 5
    SetName = 6
    CheckColor = 7
    SetColor = 8
    SetHat = 9
    SetSkin = 10
    ReportDeadBody = 11
    MurderPlayer = 12
    SendChat = 13
    StartMeeting = 14
    SetScanner = 15
    SendChatNote = 16
    SetPet = 17
    SetStartCounter = 18
    EnterVent = 19
    ExitVent = 20
    SnapTo = 21
    Close = 22
    VotingComplete = 23
    CastVote = 24
    ClearVote = 25
    AddVote = 26
    CloseDoorsOfType = 27
    RepairSystem = 28
    SetTasks = 29
    UpdateGameData = 30


class SpawnTag(AmongUsEnum):
    none = 0
    IsClientCharacter = 1
