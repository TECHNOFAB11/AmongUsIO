#!/usr/bin/python3
# -*- coding: utf-8 -*-
import struct
from dataclasses import dataclass
from typing import List

from .enums import GameSettings
from .helpers import intToGameName, pack, unpack
from .player import PlayerList


class Game:

    """
    Game object which contains the game's settings, players and more

    Attributes:
        players (PlayerList): The players which are in this game
        version (int): The version of the game (1-4) which enables the newer features
        maxPlayers (int): The max amount of players which can join this game
        keywords (GameSettings.Keywords): The keywords (language) of the game
        mapId (GameSettings.Map): The selected map for this game
        playerSpeedMod (int): The player speed multiplier
        crewLightMod (int): The crewmate vision multiplier
        impostorLightMod (int): The impostor vision multiplier
        killCooldown (int): The kill cooldown
        commonTasks (int): The amount of common tasks
        longTasks (int): The amount of long tasks
        shortTasks (int): The amount of short tasks
        emergencyMeetings (int): The amount of possible emergency meetings
        impostors (int): The amount of impostors
        killDistance (GameSettings.KillDistances): The kill distance for the impostor
        discussionTime (int): The discussion/meeting time
        votingTime (int): The voting time
        default (bool): If the settings are the default ones
        emergencyCooldown (int): The cooldown for emergency meetings
        confirmImpostor (bool): If the impostor should be revealed upon vote kill
        visualTasks (bool): If tasks that visually can prove the person as crewmate
            should be enabled (more info: https://among-us.fandom.com/wiki/Visual_Tasks)
        anonymousVotes (bool): If the votes should be anonymous/grey
        taskBarUpdates (GameSettings.TaskBarUpdate): Whether the task bar updates
            never, always or just upon meeting calls
        host (str): the hostname of the lobby
        port (int): the port of the lobby
        playerCount (int): The amount of players in this game
        name (str): The game name (visible when searching games)
        code (int): The game's code (6 chars)
        public (bool): If the game is public and thus can be found by everyone

    """

    players: PlayerList
    version: int
    maxPlayers: int
    keywords: GameSettings.Keywords
    mapId: GameSettings.Map
    playerSpeedMod: int
    crewLightMod: int
    impostorLightMod: int
    killCooldown: int
    commonTasks: int
    longTasks: int
    shortTasks: int
    emergencyMeetings: int
    impostors: int
    killDistance: GameSettings.KillDistances
    discussionTime: int
    votingTime: int
    default: bool
    emergencyCooldown: int
    confirmImpostor: bool
    visualTasks: bool
    anonymousVotes: bool
    taskBarUpdates: GameSettings.TaskBarUpdate

    host: str
    port: int
    playerCount: int
    name: str
    code: int

    public: bool

    @property
    def readable_code(self) -> str:
        return intToGameName(self.code) if hasattr(self, "code") else None

    @classmethod
    def deserialize(cls, data: bytes):
        game = cls()
        game.version = data[0]
        game.maxPlayers = data[1]
        game.keywords = GameSettings.Keywords(unpack({data[2:6]: "I"}))
        game.mapId = GameSettings.Map(data[6])
        game.playerSpeedMod = unpack({data[7:11]: "f"})
        game.crewLightMod = unpack({data[11:15]: "f"})
        game.impostorLightMod = unpack({data[15:19]: "f"})
        game.killCooldown = unpack({data[19:23]: "f"})
        game.commonTasks = data[23]
        game.longTasks = data[24]
        game.shortTasks = data[25]
        game.emergencyMeetings = unpack({data[26:30]: "I"})
        game.impostors = data[30]
        game.killDistance = GameSettings.KillDistances(data[31])
        game.discussionTime = unpack({data[32:36]: "I"})
        game.votingTime = unpack({data[36:40]: "I"})
        game.default = bool(data[40])

        if game.version > 1:
            game.emergencyCooldown = data[41]
        if game.version > 2:
            game.confirmImpostor = bool(data[42])
            game.visualTasks = bool(data[43])
        if game.version > 3:
            game.anonymousVotes = bool(data[44])
            game.taskBarUpdates = GameSettings.TaskBarUpdate(data[45])
        return game

    @classmethod
    def with_default_settings(cls):
        game = cls()
        game.version = 2
        game.maxPlayers = 10
        game.keywords = GameSettings.Keywords.All
        game.mapId = GameSettings.Map.Skeld
        game.playerSpeedMod = 1.0
        game.crewLightMod = 1.0
        game.impostorLightMod = 1.5
        game.killCooldown = 15.0
        game.commonTasks = 1
        game.longTasks = 1
        game.shortTasks = 2
        game.emergencyMeetings = 1
        game.impostors = 1
        game.killDistance = GameSettings.KillDistances.Normal
        game.discussionTime = 15
        game.votingTime = 120
        game.default = True
        game.emergencyCooldown = 15
        game.confirmImpostor = True
        game.visualTasks = True
        game.anonymousVotes = False
        game.taskBarUpdates = GameSettings.TaskBarUpdate.Always
        return game

    def serialize(self) -> bytes:
        data = (
            bytes([self.version, self.maxPlayers])
            + pack({self.keywords: "I"})
            + bytes([self.mapId])
            + struct.pack(
                "ffff",
                self.playerSpeedMod,
                self.crewLightMod,
                self.impostorLightMod,
                self.killCooldown,
            )
            + bytes([self.commonTasks, self.longTasks, self.shortTasks])
            + pack({self.emergencyMeetings: "I"})
            + bytes([self.impostors, self.killDistance])
            + pack({self.discussionTime: "I", self.votingTime: "I"})
            + bytes([self.default])
        )
        if self.version > 1:
            data += bytes([self.emergencyCooldown])
        if self.version > 2:
            data += bytes([self.confirmImpostor, self.visualTasks])
        if self.version > 3:
            data += bytes([self.anonymousVotes, self.taskBarUpdates])
        return data

    def __repr__(self):
        """
        Goes through all attributes and displays them if they're not callable or
        builtins starting with '__'

        By adding attributes to the `ignore` list you can prevent them from being shown
        """
        ignore = []
        items = []
        for item in dir(self):
            val = getattr(self, item)
            if not callable(val) and not item.startswith("__") and item not in ignore:
                items.append(f"{item}={val}")
        return f"<{self.__class__.__name__} {', '.join(items)}>"

    async def join(self):
        raise RuntimeError(
            "Cannot join game, please use Connection.join_lobby yourself"
        )


@dataclass
class GameList:
    games: List[Game]
    skeld_count: int
    mirahq_count: int
    polus_count: int
