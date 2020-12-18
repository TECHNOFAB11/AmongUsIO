#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from ...enums import GameDataTag
from ...helpers import readPacked, formatHex
from ...packets import GameDataPacket

logger = logging.getLogger(__name__)


class SpawnPacket(GameDataPacket):
    tag = GameDataTag.SpawnFlag

    @classmethod
    def create(cls, *args, **kwargs) -> "SpawnPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SpawnPacket":
        result = None
        spawn_id, _data = readPacked(data)
        owner, _data = readPacked(_data)
        flags = _data[0]
        component_length, _data = readPacked(_data[1:])

        packet = cls(data, owner=owner, flags=flags, component_length=component_length)

        for p in SpawnPacket.__subclasses__():
            if p.tag == spawn_id:
                result = p.parse(_data)
                break

        if result is not None:
            packet.add_packet(result)
        else:
            logger.debug(f"Could not find a Spawn packet which can parse '{spawn_id}'")
            logger.debug(f"Data: {formatHex(_data)}")
        return packet

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
