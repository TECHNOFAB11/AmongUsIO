#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SendChatNotePacket(RPCPacket):
    tag = RPCTag.SendChatNote

    @classmethod
    def create(cls, *args, **kwargs) -> "SendChatNotePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SendChatNotePacket":
        player_id = data[0]
        note_type = data[1]
        return cls(data, player_id=player_id, note_type=note_type)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
