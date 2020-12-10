#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ..base import Packet
from ...enums import MatchMakingTag


class ReselectServerPacket(Packet):
    tag = MatchMakingTag.ReselectServer

    @classmethod
    def parse(cls, data: bytes):
        return cls(data), b""
