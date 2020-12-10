#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import Packet
from ..enums import PacketType, DisconnectReason
from ..helpers import unpack


class DisconnectPacket(Packet):
    tag = PacketType.Disconnect

    @classmethod
    def create(cls) -> "Packet":
        return cls(b"")

    @classmethod
    def parse(cls, data: bytes):
        if len(data) == 0:
            return cls(data, reason=None), b""
        _, size = unpack({data[0:2]: "h", data[2:4]: ">h"})
        # no idea what the first thing is. Also, second one probably isnt size as its
        # sometimes 0, but also no idea why //TODO
        reason = DisconnectReason(data[4])

        args = {"reason": reason}
        if reason == DisconnectReason.Custom:
            args.update(custom_reason=data[4:].decode("UTF-8"))

        return cls(data, **args), b""

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag])
