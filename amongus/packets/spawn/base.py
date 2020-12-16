#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from amongus.enums import GameDataTag
from amongus.packets import Packet

logger = logging.getLogger(__name__)


class SpawnPacket(Packet):
    tag = GameDataTag.SpawnFlag

    @classmethod
    def create(cls, *args, **kwargs) -> "SpawnPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "SpawnPacket":
        result = None
        tag = data[0]

        for p in SpawnPacket.__subclasses__():
            if p.tag == tag:
                result = [p.parse(data)]
                break

        if result is None:
            logger.debug(f"Could not find a Spawn packet which can parse '{tag}'")
            logger.debug(
                f"Available packets: "
                f"{', '.join(p.__name__ for p in SpawnPacket.__subclasses__())}"
            )
        return cls(data)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
