#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from collections import defaultdict
from typing import Dict, List


class EventBus:
    listeners: Dict[str, List[callable]] = defaultdict(lambda: [])

    def add_listener(self, event: str, callback: callable):
        self.listeners[event].append(callback)

    def remove_listener(self, callback: callable):
        for event, callbacks in self.listeners.items():
            if callback in callbacks:
                callbacks.pop(callback)

    def dispatch(self, event: str, *args, **kwargs):
        for cb in self.listeners["on_" + event]:
            asyncio.create_task(cb(*args, **kwargs))
