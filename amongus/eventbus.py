#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    listeners: Dict[str, List[callable]] = defaultdict(lambda: [])

    def add_listener(self, event: str, callback: callable):
        self.listeners[event].append(callback)

    def remove_listener(self, callback: callable):
        for _, callbacks in self.listeners.items():
            if callback in callbacks:
                callbacks.pop(callback)

    def dispatch(self, event: str, *args, **kwargs):
        if asyncio.get_event_loop().get_debug():
            logger.debug(f"Dispatching event (on_) '{event}'")
        for cb in self.listeners["on_" + event]:
            asyncio.create_task(cb(*args, **kwargs))
