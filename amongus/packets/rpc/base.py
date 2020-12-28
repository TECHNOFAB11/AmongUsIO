#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging

from ...enums import GameDataTag
from ...helpers import createPacked, formatHex, readPacked
from ...packets import GameDataPacket

logger = logging.getLogger(__name__)


class RPCPacket(GameDataPacket):
    tag = GameDataTag.RpcFlag

    @classmethod
    def create(cls, contained_packets: list, net_id: int) -> "RPCPacket":
        return cls(b"", contained_packets=contained_packets or [], net_id=net_id)

    @classmethod
    def parse(cls, data: bytes) -> "RPCPacket":
        result = None
        net_id, _data = readPacked(data[0:])
        tag = _data[0]

        for p in RPCPacket.__subclasses__():
            if p.tag == tag:
                result = [p.parse(_data[1:])]
                break

        if result is None:
            logger.debug(f"Could not find a RPC packet which can parse '{tag}'")
            logger.debug(f"Data: {formatHex(_data[1:])}")
        return cls(data, net_id=net_id, contained_packets=result)

    def serialize(self, getID: callable) -> bytes:
        return (
            bytes([self.tag])
            + createPacked(self.values.net_id)
            + b"".join([p.serialize(getID) for p in self.contained_packets])
        )
