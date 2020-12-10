#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import Packet
from ..enums import PacketType
from ..helpers import pack


def convertGameVersion(version: tuple) -> int:
    return (
        (version[0] * 25000)
        + (version[1] * 1800)
        + (version[2] * 50)
        + (version[3] if len(version) == 4 else 0)
    )


class HelloPacket(Packet):
    tag = PacketType.Hello

    @classmethod
    def create(cls, gameVersion: tuple, name: str) -> "Packet":
        return cls(b"", gameVersion=gameVersion, name=name)

    @classmethod
    def parse(cls, data: bytes) -> "Packet":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        version = convertGameVersion(self.values.gameVersion)
        return (
            bytes([self.tag, 0])
            + pack({getID(): "h", version: "I"})
            + bytes([len(self.values.name)])
            + bytes(self.values.name.encode())
        )
