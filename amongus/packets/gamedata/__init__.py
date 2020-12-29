#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
All :class:`GameDataTag` packets
"""

from .base import GameDataPacket
from .scenechange import SceneChangePacket

__all__ = [
    "GameDataPacket",
    "SceneChangePacket",
]
