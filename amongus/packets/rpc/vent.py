#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readPacked


class EnterVentPacket(RPCPacket):
    tag = RPCTag.EnterVent

    @classmethod
    def create(cls, *args, **kwargs) -> "EnterVentPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "EnterVentPacket":
        player_id, _ = readPacked(data)
        return cls(data, player_id=player_id)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError


class ExitVentPacket(RPCPacket):
    tag = RPCTag.ExitVent

    @classmethod
    def create(cls, *args, **kwargs) -> "ExitVentPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "ExitVentPacket":
        player_id, _ = readPacked(data)
        return cls(data, player_id=player_id)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
