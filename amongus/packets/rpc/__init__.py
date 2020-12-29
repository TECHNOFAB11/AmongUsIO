#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
All :class:`RPCTag` packets
"""

from .base import RPCPacket
from .checkcolor import CheckColorPacket
from .checkname import CheckNamePacket
from .sendchat import SendChatPacket
from .setcolor import SetColorPacket
from .sethat import SetHatPacket
from .setname import SetNamePacket
from .setpet import SetPetPacket
from .setskin import SetSkinPacket
from .setstartcounter import SetStartCounterPacket
from .syncsettings import SyncSettingsPacket
from .updategamedata import UpdateGameDataPacket

__all__ = [
    "RPCPacket",
    "SetStartCounterPacket",
    "SendChatPacket",
    "SyncSettingsPacket",
    "UpdateGameDataPacket",
    "CheckNamePacket",
    "CheckColorPacket",
    "SetPetPacket",
    "SetHatPacket",
    "SetSkinPacket",
    "SetNamePacket",
    "SetColorPacket",
]
