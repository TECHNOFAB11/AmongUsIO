#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import RPCPacket
from ...enums import RPCTag
from ...helpers import readPacked


class SetTasksPacket(RPCPacket):
    tag = RPCTag.SetTasks

    @classmethod
    def create(cls, *args, **kwargs) -> "SetTasksPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SetTasksPacket":
        player_id = data[0]
        size, _data = readPacked(data[1:])
        _data = bytearray(_data[:size])
        task_ids = []
        for _id in _data:
            task_ids.append(_id)
        return cls(data, player_id=player_id, task_ids=task_ids)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
