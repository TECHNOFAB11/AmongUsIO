#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple
from ..base import Packet
from ...enums import MatchMakingTag


class ReselectServerPacket(Packet):
    tag = MatchMakingTag.ReselectServer

    @classmethod
    def create(cls, *args, **kwargs) -> "ReselectServerPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["ReselectServerPacket", bytes]:
        return cls(data), b""

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
