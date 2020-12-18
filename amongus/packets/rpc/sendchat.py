#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readString, writeString


class SendChatPacket(RPCPacket):
    tag = RPCTag.SendChat

    @classmethod
    def create(cls, message: str) -> "SendChatPacket":
        return cls(b"", message=message)

    @classmethod
    def parse(cls, data: bytes) -> "SendChatPacket":
        message, _ = readString(data)
        return cls(data, message=message)

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag]) + writeString(self.values.message)
