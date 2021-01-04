#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readPacked


class VotingCompletePacket(RPCPacket):
    tag = RPCTag.VotingComplete

    @classmethod
    def create(cls, *args, **kwargs) -> "VotingCompletePacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "VotingCompletePacket":
        size, _data = readPacked(data)
        states = _data[:size]  # purpose unknown
        player_id = _data[size]
        tie = _data[size + 1]
        return cls(data, player_id=player_id, tie=tie, states=states)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
