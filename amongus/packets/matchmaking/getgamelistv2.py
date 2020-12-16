#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ..base import Packet
from ...enums import MatchMakingTag


class GetGameListV2Packet(Packet):
    tag = MatchMakingTag.GetGameListV2

    @classmethod
    def create(cls) -> "GetGameListV2Packet":
        # TODO
        return cls(b"")

    @classmethod
    def parse(cls, data: bytes) -> "GetGameListV2Packet":
        raise NotImplementedError

    def serialize(self, getID: callable) -> bytes:
        return bytes([self.tag])
