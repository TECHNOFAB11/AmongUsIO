#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import collections
from typing import Any, Callable


class PacketQueue:

    """
    A queue for incoming packets and methods to be able to handle them in multiple
    places at once
    """

    _new_content = asyncio.Event()
    _processed_content = asyncio.Event()

    def __init__(self, maxlen: int = None):
        self._content = collections.deque(maxlen=maxlen)
        self._processed_content.set()

    def clear(self):
        self._content.clear()

    async def put(self, item: Any):
        """Adds a new item to the queue"""
        await self._processed_content.wait()
        self._content.append(item)
        self._new_content.set()

    async def wait_for(
        self, packet_filter: Callable, new_only: bool = True, ignore: list = None
    ):
        """
        Waits for new packets (or finds old ones) and puts them through the
        `packet_filter`. If this filter returns True the packet gets returned

        Args:
            packet_filter (Callable): The filter through which all packets get put
            new_only (bool): If only new packets should be returned. If this is False
                old packets may be returned if they pass the filter
            ignore (list): A list of packets to ignore
        """
        ignore = ignore or []
        if not new_only:
            for item in self._content:
                if item not in ignore and packet_filter(item):
                    return item

        while True:
            await self._new_content.wait()
            self._processed_content.clear()
            try:
                item = self._content[-1]
            except IndexError:
                pass
            else:
                if packet_filter(item):
                    return item
            self._new_content.clear()
            self._processed_content.set()
