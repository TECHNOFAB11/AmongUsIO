#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import collections
from typing import Any, Callable


class PacketQueue:

    """

    """

    _new_content = asyncio.Event()
    _processed_content = asyncio.Event()

    def __init__(self, maxlen: int = None):
        self._content = collections.deque(maxlen=maxlen)
        self._processed_content.set()

    def clear(self):
        self._content.clear()

    async def put(self, item: Any):
        """

        """
        await self._processed_content.wait()
        self._content.append(item)
        self._new_content.set()

    async def wait_for(
        self, filter: Callable, new_only: bool = True, ignore: list = []
    ):
        """

        """
        if not new_only:
            for item in self._content:
                if item not in ignore and filter(item):
                    return item

        while True:
            await self._new_content.wait()
            self._processed_content.clear()
            try:
                item = self._content[-1]
            except IndexError:
                pass
            else:
                if filter(item):
                    return item
            self._new_content.clear()
            self._processed_content.set()
