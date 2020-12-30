#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Union

from .enums import PlayerAttributes
from .helpers import dotdict, readPacked, readString
from .task import Task


class Player:

    """Represents an Among Us player

    Attributes:
        id (int): The player id
        name (str): The player's name
        color (PlayerAttributes.Color): The player's color
        hatId (PlayerAttributes.Hat): The player's hat
        petId (PlayerAttributes.Pet): The player's pet
        skinId (PlayerAttributes.Skin): The player's skin
        statusBitField (int): ? TODO
        tasks (List[Task]): A list of the player's tasks
        net_id (int): The player's net id
    """

    id: int  # noqa: A003
    name: str
    color: PlayerAttributes.Color
    hatId: PlayerAttributes.Hat
    petId: PlayerAttributes.Pet
    skinId: PlayerAttributes.Skin
    statusBitField: int
    tasks: List[Task]
    net_ids: dotdict
    position: Tuple[int, int]
    velocity: Tuple[int, int]

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} id={self.id}, name={self.name}, "
            f"net_ids={self.net_ids}, color={self.color}, tasks="
            f"[{', '.join(self.tasks)}]>"
        )

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple["Player", bytes]:
        player = cls()
        player.net_ids = {"control": None, "physics": None, "network": None}
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

    """A class to manage players

    Attributes:
        players (Dict[int, Player]): The players in this PlayerList, this attribute
            should not be needed directly
    """

    players: Dict[int, Player]

    def __init__(self):
        """Creates a new PlayerList with no players"""
        self.players = {}

    def __repr__(self):
        """Show the attributes in a readable form"""
        return f"<{self.__class__.__name__} players={self.players}>"

    def __contains__(self, item: int) -> bool:
        """If this PlayerList contains a player_id"""
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
        """Makes it possible to iterate over this PlayerList"""
        return iter(self.players.values())

    def __getitem__(self, player_id: int) -> Player:
        """Returns a player by it's player_id"""
        return self.players.get(player_id)

    def __len__(self) -> int:
        """Returns the amount of players in this PlayerList"""
        return len(self.players)

    def from_net_id(self, net_id: int) -> Player:
        """Returns a player by its net_id or None if no player was found"""
        players = list(
            filter(lambda p: net_id in p.net_ids.values(), self.players.values())
        )
        return players[0] if len(players) else None

    def complete(self) -> bool:
        """Returns True if all player's net_id's are known and thus ready"""
        return all([player.net_id is not None for player in self.players.values()])
