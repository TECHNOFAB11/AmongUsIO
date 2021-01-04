#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from typing import List

from .. import Packet
from ..gamedata.base import GameDataPacket
from ...enums import DataFlag, GameDataTag
from ...helpers import createPacked, formatHex, readPacked

logger = logging.getLogger(__name__)


class DataFlagPacket(GameDataPacket):
    tag = GameDataTag.DataFlag

    @classmethod
    def create(cls, contained_packets: List[Packet], net_id: int) -> "DataFlagPacket":
        return cls(b"", net_id=net_id, contained_packets=contained_packets)

    @classmethod
    def parse(cls, data: bytes) -> "DataFlagPacket":
        net_id, _data = readPacked(data)
        p = cls(data, net_id=net_id, child_data=_data)
        return p

    def parse_with_flag(self, dataflag: DataFlag):
        """
        As net_ids are not unique and dont directly tell us what type they represent
        (movement, sabotage etc.), we have to check which parser we need in
        :class:`Connection` and then run this to continue the "parsing pipeline"

        Args:
            dataflag (DataFlag): Our internal dataflag enum for "translation"
        """
        result = None
        for p in DataFlagPacket.__subclasses__():
            if p.tag == dataflag:
                result = p.parse(self.values.child_data)

        if result is not None:
            self.add_packet(result)
        else:
            logger.warning(
                f"Could not find a DataFlag packet which can parse '{dataflag}'.\n"
                f"Data: {formatHex(self.values.child_data)}"
            )

    def serialize(self, getID: callable) -> bytes:
        rest = b"".join(p.serialize(getID) for p in self.contained_packets)
        return bytes([self.tag]) + createPacked(self.values.net_id) + rest
