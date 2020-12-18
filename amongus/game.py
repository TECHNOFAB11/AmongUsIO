#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .player import PlayerList


class Game:
    players: PlayerList
    version: int
    maxPlayers: int
    keywords: int
    mapId: int
    playerSpeedMod: int
    crewLightMod: int
    impostorLightMod: int
    killCooldown: int
    commonTasks: int
    longTasks: int
    shortTasks: int
    emergencyMeetings: int
    impostors: int
    killDistance: int
    discussionTime: int
    votingTime: int
    default: bool
    emergencyCooldown: int
    confirmImpostor: bool
    visualTasks: bool
    anonymousVotes: bool
    taskBarUpdates: int

    def __init__(self):
        pass
