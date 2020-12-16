#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from amongus.enums import GameDataTag
from amongus.helpers import readPacked
from amongus.packets import GameDataPacket

logger = logging.getLogger(__name__)


class RPCPacket(GameDataPacket):
    tag = GameDataTag.RpcFlag

    @classmethod
    def create(cls, *args, **kwargs) -> "RPCPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> "RPCPacket":
        result = None
        target_net_id, _data = readPacked(data[0:])
        tag = _data[0]

        for p in RPCPacket.__subclasses__():
            if p.tag == tag:
                result = [p.parse(data)]
                break

        if result is None:
            logger.debug(f"Could not find a RPC packet which can parse '{tag}'")
            logger.debug(
                f"Available packets: "
                f"{', '.join(p.__name__ for p in RPCPacket.__subclasses__())}"
            )
        return cls(data, target_net_id=target_net_id, contained_packets=result)

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
