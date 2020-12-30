#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .base import Packet
from ..enums import DisconnectReason, PacketType
from ..helpers import readMessage


class DisconnectPacket(Packet):
    tag = PacketType.Disconnect

    @classmethod
    def create(cls) -> "DisconnectPacket":
        return cls(b"")

    @classmethod
    def parse(cls, data: bytes) -> Tuple["DisconnectPacket", bytes]:
        if len(data) == 0:
            return cls(data, reason=None), b""
        _, _data, _ = readMessage(data)
        reason = DisconnectReason(_data[1])
        custom_reason = None
        if reason == DisconnectReason.Custom:
            size = _data[2]
            custom_reason = _data[3 : 3 + size].decode()

        return cls(data, reason=reason, custom_reason=custom_reason), b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag])
