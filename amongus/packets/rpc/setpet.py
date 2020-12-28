#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class SetPetPacket(RPCPacket):
    tag = RPCTag.SetPet

    @classmethod
    def create(cls, pet: int) -> "SetPetPacket":
        return cls(b"", pet=pet)

    @classmethod
    def parse(cls, data: bytes) -> "SetPetPacket":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag, self.values.pet])
