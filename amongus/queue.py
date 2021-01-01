#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import collections
from typing import Any, Callable, Dict


class PacketQueue:
    """
    A queue for incoming packets and methods to be able to handle them in multiple
    places at once
    """

    _listeners: Dict[callable, callable] = {}

    def __init__(self, maxlen: int = None):
        """
        Initializes the queue

        Args:
            maxlen (int): If given the queue has a limited length and everything
                beyond that length will be deleted (LOFI)
        """
        self._content = collections.deque(maxlen=maxlen)

    def clear(self):
        self._content.clear()

    async def put(self, item: Any):
        """Adds a new item to the queue."""
        _run = []
        self._content.append(item)
        for _filter, callback in self._listeners.items():
            if _filter(item):
                _run.append(callback(item))
        if len(_run):
            await asyncio.gather(*_run)

    async def add_listener(self, packet_filter: callable, callback: callable):
        """
        Adds a listener whose callback will be called if a new packet passes the
        packet_filter
        """
        self._listeners[packet_filter] = callback

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

        _new_content = asyncio.Event()
        _data: Any = None

        async def callback(item: Any):
            nonlocal _data
            _new_content.set()
            _data = item

        await self.add_listener(packet_filter, callback)
        await _new_content.wait()
        return _data
