#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from typing import Tuple

from ...enums import MatchMakingTag
from ...helpers import createPacked, formatHex, pack, readPacked, unpack
from ...packets import Packet

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
        _data = data[4:]
        while len(_data):
            size = unpack({_data[:2]: "h"})
            tag = _data[2]
            result = None

            for p in GameDataPacket.__subclasses__():
                if p.tag == tag:
                    result = p.parse(_data[3 : size + 3])
                    break

            if result is not None:
                packet.add_packet(result)
            else:
                logger.debug(
                    f"Could not find a GameData packet which can parse '{tag}'"
                )
                logger.debug(f"Data: {formatHex(_data[3 : size + 3])}")
            _data = _data[size + 3 :]
        return packet, b""

    def serialize(self, getID: callable) -> bytes:
        packets = [p.serialize(getID) for p in self.contained_packets]
        rest = b"".join([pack({len(data) - 1: "h"}) + data for data in packets])
        return bytes([self.tag]) + pack({self.values.game_id: "I"}) + rest


class GameDataToPacket(Packet):
    tag = MatchMakingTag.GameDataTo

    @classmethod
    def create(
        cls, contained_packets: list, game_id: int, target: int
    ) -> "GameDataToPacket":
        return cls(
            b"", game_id=game_id, contained_packets=contained_packets, target=target
        )

    @classmethod
    def parse(cls, data: bytes) -> Tuple["GameDataToPacket", bytes]:
        game_code = unpack({data[0:4]: "I"})
        target, _data = readPacked(data[4:])
        packet = cls(data, game_code=game_code, target=target)
        while len(_data):
            size = unpack({_data[:2]: "h"})
            tag = _data[2]
            result = None

            for p in GameDataPacket.__subclasses__():
                if p.tag == tag:
                    result = p.parse(_data[3 : size + 3])
                    break

            if result is not None:
                packet.add_packet(result)
            else:
                logger.debug(
                    f"Could not find a GameData packet which can parse '{tag}'"
                )
                logger.debug(f"Data: {formatHex(_data[3 : size + 3])}")
            _data = _data[size + 3 :]
        return packet, b""

    def serialize(self, getID: callable) -> bytes:
        packets = [p.serialize(getID) for p in self.contained_packets]
        rest = b"".join([pack({len(data) - 1: "h"}) + data for data in packets])
        return (
            bytes([self.tag])
            + pack({self.values.game_id: "I"})
            + createPacked(self.values.target)
            + rest
        )
