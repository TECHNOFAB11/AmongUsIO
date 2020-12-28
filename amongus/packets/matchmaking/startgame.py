#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from ..base import Packet
from ...enums import MatchMakingTag


class StartGamePacket(Packet):
    tag = MatchMakingTag.StartGame

    @classmethod
    def create(cls) -> "StartGamePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["StartGamePacket", bytes]:
        return cls(data), b""

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
