#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""All :class:`RPCTag` packets."""

from .base import RPCPacket
from .checkcolor import CheckColorPacket
from .checkname import CheckNamePacket
from .close import ClosePacket
from .murderplayer import MurderPlayerPacket
from .reportdeadbody import ReportDeadBodyPacket
from .sendchat import SendChatPacket
from .sendchatnote import SendChatNotePacket
from .setcolor import SetColorPacket
from .sethat import SetHatPacket
from .setinfected import SetInfectedPacket
from .setname import SetNamePacket
from .setpet import SetPetPacket
from .setscanner import SetScannerPacket
from .setskin import SetSkinPacket
from .setstartcounter import SetStartCounterPacket
from .settasks import SetTasksPacket
from .snapto import SnapToPacket
from .startmeeting import StartMeetingPacket
from .syncsettings import SyncSettingsPacket
from .updategamedata import UpdateGameDataPacket
from .votingcomplete import VotingCompletePacket

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
    "SetInfectedPacket",
    "SetTasksPacket",
    "MurderPlayerPacket",
    "ReportDeadBodyPacket",
    "StartMeetingPacket",
    "VotingCompletePacket",
    "ClosePacket",
    "SnapToPacket",
    "SendChatNotePacket",
    "SetScannerPacket",
]
