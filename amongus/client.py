#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import re
from ipaddress import ip_address
from typing import Any, Union, Callable
from amongus.eventbus import EventBus
from amongus.exceptions import AmongUsException
from amongus.connection import Connection
from amongus.regions import regions


class Client:
    """
    The main client used to interact with the Among Us servers

    Attributes:
        name (str): The current name of the user
        stopped (bool): If the client is stopped (= connection closed)
        lobby_code (str): The current game lobby code (normally 6 chars long)
        region (str): The current region to which the client is connected to
    """

    name: str
    connection: Connection
    eventbus: EventBus

    def __init__(self, name: str):
        """
        Client used to interact with the Among Us servers

        Args:
            name (str): Name which is shown in the game for this Client
            stopped (bool): If the client is stopped/the connection closed
            lobby_code (str): The current lobby code
            region (str): The currrent region

        Raises:
            AmongUsException: Name is longer than 10 or shorter than 1 characters
        """
        if 0 == len(name) > 10:
            raise AmongUsException(
                "Name can't be longer than 10 or shorter than 1 character(s)!"
            )
        self.name = name
        self.eventbus = EventBus()
        self.connection = Connection(self.eventbus)

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
                see amongus.regions.regions
            custom_server (str): Optional; A custom address to connect to, either this
                or region has to be given. Example: `10.1.1.1:22023` or `10.1.1.1`

        Raises:
            ConnectionException: Server disconnected,
                see :attr:`ConnectionException.reason` for the reason and
                :attr:`ConnectionException.custom_reason` if the reason is "Custom"
            AmongUsException: Invalid region
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
            except ValueError:
                # just let the user handle it
                raise
        else:
            host = regions[region]
            port = 22023

        try:
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

    async def find_games(self) -> list:
        """
        Returns the currently open games/lobbies

        TODO
        """
        pass

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
