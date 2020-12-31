#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import re
from ipaddress import ip_address
from typing import Any, Callable, Tuple, Union

from .connection import Connection
from .enums import GameSettings, PlayerAttributes
from .eventbus import EventBus
from .exceptions import AmongUsException
from .game import GameList
from .regions import regions


class Client:
    """The main client used to interact with the Among Us servers

    Attributes:
        name (str): The current name of the user
        stopped (bool): If the client is stopped (= connection closed)
        lobby_code (str): The current game lobby code (normally 6 chars long)
        region (str): The current region to which the client is connected to
        color (PlayerAttributes.Color): Color of the character
        hat (PlayerAttributes.Hat): Hat of the character
        skin (PlayerAttributes.Skin): Skin of the character
        pet (PlayerAttributes.Pet): Pet of the character
        spectator (bool): Whether the Client should behave like a normal player
            or just "spectate" and remain invisible
    """

    connection: Connection
    eventbus: EventBus

    def __init__(
        self,
        name: str,
        color: PlayerAttributes.Color = 0,
        hat: PlayerAttributes.Hat = 0,
        skin: PlayerAttributes.Skin = 0,
        pet: PlayerAttributes.Pet = 0,
        spectator: bool = False,
    ):
        """
        Client used to interact with the Among Us servers

        Args:
            name (str): Name which is shown in the game for this Client
            stopped (bool): If the client is stopped/the connection closed
            lobby_code (str): The current lobby code
            region (str): The currrent region
            color (PlayerAttributes.Color): Color of the character
            hat (PlayerAttributes.Hat): Hat of the character
            skin (PlayerAttributes.Skin): Skin of the character
            pet (PlayerAttributes.Pet): Pet of the character
            spectator (bool): If the client should only spectate

        Raises:
            AmongUsException: Name is longer than 10 or shorter than 1 characters
        """
        if 0 == len(name) > 10:
            raise AmongUsException(
                "Name can't be longer than 10 or shorter than 1 character(s)!"
            )
        self.eventbus = EventBus()
        self.connection = Connection(self.eventbus)
        self.name = name
        self.color = color
        self.hat = hat
        self.skin = skin
        self.pet = pet
        self.spectator = spectator

    @property
    def stopped(self) -> bool:
        return self.connection.closed

    @property
    def lobby_code(self) -> str:
        return self.connection.lobby_code

    @lobby_code.setter
    def lobby_code(self, value: str) -> None:
        self.connection.lobby_code = value

    @property
    def region(self) -> str:
        return self.connection.region

    @region.setter
    def region(self, value: str) -> None:
        self.connection.region = value

    @property
    def name(self) -> str:
        return self.connection.name

    @name.setter
    def name(self, value: str) -> None:
        self.connection.name = value

    @property
    def color(self) -> PlayerAttributes.Color:
        return self.connection.color

    @color.setter
    def color(self, value: PlayerAttributes.Color) -> None:
        self.connection.color = value

    @property
    def hat(self) -> PlayerAttributes.Hat:
        return self.connection.hat

    @hat.setter
    def hat(self, value: PlayerAttributes.Hat) -> None:
        self.connection.hat = value

    @property
    def skin(self) -> PlayerAttributes.Skin:
        return self.connection.skin

    @skin.setter
    def skin(self, value: PlayerAttributes.Skin) -> None:
        self.connection.skin = value

    @property
    def pet(self) -> PlayerAttributes.Pet:
        return self.connection.pet

    @pet.setter
    def pet(self, value: PlayerAttributes.Pet) -> None:
        self.connection.pet = value

    @property
    def spectator(self) -> bool:
        return self.connection.spectator

    @spectator.setter
    def spectator(self, value: bool) -> None:
        self.connection.spectator = value

    @property
    def latency(self) -> int:
        return self.connection.latency

    @property
    def _result(self) -> Any:
        return self.connection.result

    def run(self, *args, **kwargs) -> Any:
        """
        Helper function which runs :meth:`Client.start`

        All arguments will be passed to :meth:`Client.start`,
        this will block until the connection is closed from either side
        """
        return asyncio.get_event_loop().run_until_complete(self.start(*args, **kwargs))

    def add_listener(self, event: str, func: Callable) -> None:
        """
        This adds a listener to the eventbus

        Args:
            event (str): The event to listen/subscribe to
            func (Callable): The callback which will be run when the event happens

        Raises:
            TypeError: The callback is not a coroutine
        """
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Listeners must be coroutines")

        name = event if event is not None else func.__name__
        if not name.startswith("on_"):
            name = "on_" + name
        self.eventbus.add_listener(name, func)

    def remove_listener(self, func: Callable) -> None:
        """
        Removes an event listener, doesn't do anything when it doesn't exist

        Args:
            func (Callable): The callback which should be removed as a listener
        """
        self.eventbus.remove_listener(func)

    def event(self, name: Union[str, Callable] = None) -> Callable:
        """
        Decorator for :meth:`Client.add_listener`

        Args:
            name (str): Optional; The event name to listen on, if not given the
                function name will be used
        """

        def decorator(func: Callable):
            _name = name
            if callable(_name):
                _name = name.__name__
                func = name
            self.add_listener(_name, func)
            return func

        return decorator(name) if callable(name) else decorator

    async def start(self, region: str = None, custom_server: str = None) -> Any:
        """
        Starts the client, connecting to the server and sleeping until disconnect

        Args:
            region (str): Optional; The region where the lobby is hosted,
                see :attr:`amongus.regions.regions`
            custom_server (str): Optional; A custom address to connect to, either this
                or region has to be given. Example: `10.1.1.1:22023` or `10.1.1.1`

        Raises:
            ConnectionException: Server disconnected,
                see :attr:`ConnectionException.reason` for the reason and
                :attr:`ConnectionException.custom_reason` if the reason is "Custom"
            AmongUsException: Invalid region or custom_server could not be parsed
        """
        if region is not None and region.upper() not in regions:
            raise AmongUsException(f"The region {region} does not exist!")

        self.region = region

        if custom_server is not None:
            host, s, port = custom_server.rpartition(":")
            if not s:
                host = port
                port = 22023
            try:
                _ = ip_address(host)
                port = int(port)
            except ValueError as e:
                # just let the user handle it
                raise AmongUsException("custom_server ip could not be parsed!") from e
        else:
            host = regions[region]
            port = 22023

        try:
            self.connection.players.ready = False
            await self.connection.connect(name=self.name, host=host, port=port)

            while not self.stopped:
                # only exit when we lost connection or disconnected in some other way
                await asyncio.sleep(1)

            if isinstance(self._result, Exception):
                raise self._result
            else:
                return self._result
        finally:
            await self.stop()

    async def join_lobby(self, lobby_code: str) -> bool:
        """
        Joins an existing lobby

        Args:
            lobby_code (str): 6 or 4 digit lobby code from Among Us

        Raises:
            AmongUsException: Invalid lobby code
        """
        if len(lobby_code) not in [4, 6]:
            raise AmongUsException("Invalid lobby code length!")
        if re.match("^[A-Z]*$", lobby_code.upper()) is None:
            raise AmongUsException("The lobby code can only contain letters!")
        self.lobby_code = lobby_code.upper()
        return await self.connection.join_game(self.lobby_code)

    async def find_games(
        self,
        mapId: GameSettings.Map = GameSettings.Map.All,
        impostors: int = 0,
        language: GameSettings.Keywords = GameSettings.Keywords.All,
    ) -> GameList:
        """
        Returns the currently open games/lobbies

        Args:
            mapId (GameSettings.Map): The wanted map
            impostors (int): Amount of impostors (0-3, 0 being Any)
            language (GameSettings.Keywords): Which language the chat should be

        Returns:
            :class:`GameList`

        Raises:
            AmongUsException: Amount of impostors is not between 0 and 3
        """
        if impostors not in range(3):
            raise AmongUsException("Amount of impostors has to be between 0 and 3!")
        return await self.connection.find_games(mapId, impostors, language)

    async def stop(self, force: bool = False) -> None:
        """
        Stops the client

        Informs the server before disconnecting if force is False

        Args:
            force (bool): Will just close the connection if True, otherwise it will
                inform the server first
        """
        await self.connection.disconnect(force)

    async def send_chat(self, message: str) -> None:
        """
        Sends a chat message to the server

        Args:
            message (str): The message to send
        """
        await self.connection.send_chat(message)

    async def move(self, position: Tuple[int, int], velocity: Tuple[int, int]) -> None:
        """
        Moves the player to the given position

        Args:
            position (Tuple[int, int]): A tuple of x, y coordinates to move to
            velocity (Tuple[int, int]): A tuple of x, y coordinates with the
                velocity/relative position
        """
        await self.connection.move(position, velocity)
