#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag


class ReportDeadBodyPacket(RPCPacket):
    tag = RPCTag.ReportDeadBody

    @classmethod
    def create(cls, *args, **kwargs) -> "ReportDeadBodyPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "ReportDeadBodyPacket":
        return cls(data, player_id=data[0])

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
