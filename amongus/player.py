#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Union

from .helpers import readPacked, readString
from .task import Task


class Player:
    id: int  # noqa: A003
    name: str
    color: int
    hatId: int
    petId: int
    skinId: int
    statusBitField: int
    tasks: List[Task]
    net_id: int

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} id={self.id}, name={self.name}, "
            f"net_id={self.net_id}, color={self.color}, tasks="
            f"[{', '.join(self.tasks)}]>"
        )

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple["Player", bytes]:
        player = cls()
        player.net_id = None
        player.id = data[0]
        player.name, _data = readString(data[1:])
        player.color = _data[0]
        player.hatId, _data = readPacked(_data[1:])
        player.petId, _data = readPacked(_data)
        player.skinId, _data = readPacked(_data)
        player.statusBitField = _data[0]
        task_amount = _data[1]
        player.tasks = []
        _data = _data[2:]
        for _ in range(task_amount):
            t, _data = Task.deserialize(_data)
            player.tasks.append(t)
        return player, _data

    def serialize(self) -> bytes:
        pass


class PlayerList:
    players: Dict[int, Player]

    def __init__(self):
        self.players = {}

    def __repr__(self):
        return f"<{self.__class__.__name__} players={self.players}>"

    def __contains__(self, item: int):
        return item in self.players.keys()

    def __iadd__(self, other: Union[Player, list]):
        """
        Adds a new player or list of players to this PlayerList

        Example:
            .. code-block:: python

               players = PlayerList()
               players += [Player(...), Player(...)]
        """
        if type(other) == list:
            for player in other:
                self.players.update({player.id: player})
        elif type(other) == Player:
            self.players.update({other.id: other})
        return self

    def __iter__(self):
        return iter(self.players.values())

    def __getitem__(self, player_id: int):
        return self.players.get(player_id)

    def __len__(self):
        return len(self.players)

    def from_net_id(self, net_id: int):
        players = list(filter(lambda p: p.net_id == net_id, self.players.values()))
        return players[0] if len(players) else None

    def complete(self):
        return all([player.net_id is not None for player in self.players.values()])
