#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from typing import Tuple
from amongus.enums import MatchMakingTag
from amongus.helpers import unpack, pack
from amongus.packets import Packet

logger = logging.getLogger(__name__)


class GameDataPacket(Packet):
    tag = MatchMakingTag.GameData

    @classmethod
    def create(cls, contained_packets: list, game_id: int) -> "GameDataPacket":
        return cls(b"", game_id=game_id, contained_packets=contained_packets)

    @classmethod
    def parse(cls, data: bytes) -> Tuple["GameDataPacket", bytes]:
        game_code = unpack({data[0:4]: "I"})
        packet = cls(data, game_code=game_code)
        data = data[4:]
        while len(data):
            size = unpack({data[:2]: "h"})
            tag = data[2]
            result = None

            for p in GameDataPacket.__subclasses__():
                if p.tag == tag:
                    result = p.parse(data[3 : size + 3])
                    break

            if result is not None:
                packet.contained_packets.append(result)
            else:
                logger.debug(
                    f"Could not find a GameData packet which can parse '{tag}'"
                )
                logger.debug(
                    f"Available packets: "
                    f"{', '.join(p.__name__ for p in GameDataPacket.__subclasses__())}"
                )
            data = data[size + 3 :]
        return packet, b""

    def serialize(self, getID: callable) -> bytes:
        packets = [p.serialize(getID) for p in self.contained_packets]
        rest = b"".join([pack({len(data) - 1: "h"}) + data for data in packets])
        return bytes([self.tag]) + pack({self.values.game_id: "I"}) + rest
