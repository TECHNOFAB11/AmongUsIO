#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import re
from typing import Any, Union, Callable

from amongus.eventbus import EventBus
from amongus.exceptions import AmongUsException
from amongus.connection import Connection
from amongus.regions import regions


class Client:
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
        Helper function which runs :meth:Client.start

        All arguments will be passed to :meth:Client.start
        This will block until the connection is closed from either side
        """
        return asyncio.get_event_loop().run_until_complete(self.start(*args, **kwargs))

    def add_listener(self, event: str, func: Callable):
        """

        """
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Listeners must be coroutines")

        name = event if event is not None else func.__name__
        if not name.startswith("on_"):
            name = "on_" + name
        self.eventbus.add_listener(name, func)

    def event(self, name: Union[str, Callable] = None):
        """

        """

        def decorator(func: Callable):
            _name = name
            if callable(_name):
                _name = name.__name__
                func = name
            self.add_listener(_name, func)
            return func

        return decorator(name) if callable(name) else decorator

    async def start(self, region: str) -> Any:
        """
        Starts the client, connecting to the server and sleeping until disconnect

        Args:
            region (str): The region where the lobby is hosted,
                see amongus.regions.regions

        Raises:
            ConnectionException: Server disconnected, see ConnectionException.reason
                for the reason and ConnectionException.custom_reason
                if the reason is "Custom"
            AmongUsException: Invalid region
        """
        if region.upper() not in regions:
            raise AmongUsException(f"The region {region} does not exist!")

        self.region = region
        try:
            await self.connection.connect(
                name=self.name, host=regions[region], port=22023
            )

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

    async def find_games(self):
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
