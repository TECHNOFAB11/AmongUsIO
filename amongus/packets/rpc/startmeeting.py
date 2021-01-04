#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readPacked


class StartMeetingPacket(RPCPacket):
    tag = RPCTag.StartMeeting

    @classmethod
    def create(cls, *args, **kwargs) -> "StartMeetingPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "StartMeetingPacket":
        player_id, _ = readPacked(data)
        return cls(data, player_id=player_id)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
