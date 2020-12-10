#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from typing import List

from amongus.enums import PacketType

logger = logging.getLogger(__name__)


class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Packet:
    """

    """

    data: bytes
    tag: int = None
    contained_packets: list = []
    values: dotdict = dotdict()
    reliable_id: int = None

    def __init__(self, data: bytes, tag: int = None, base: "Packet" = None, **kwargs):
        self.data = data
        if tag is not None:
            self.tag = tag
        self.base = base
        self.values = dotdict(kwargs)

    def __iter__(self):
        return iter(self.contained_packets)

    def __repr__(self):
        ignore = []
        items = (f"{k}={v}" for k, v in self.__dict__.items() if k not in ignore)
        return f"<{self.__class__.__name__} {', '.join(items)}>"

    @property
    def reliable(self):
        return self.tag in [
            PacketType.Ping,
            PacketType.Acknowledgement,
            PacketType.Hello,
            PacketType.Reliable,
        ]

    @classmethod
    def create(cls, *args, **kwargs) -> "Packet":
        raise NotImplementedError

    @staticmethod
    def parse(data: bytes) -> List["Packet"]:
        """
        Parses bytes and yields the contained packets

        Note:
            Each packet type should overwrite this and handle the data for their
            specific tag/id
        """
        packets = []
        while len(data):
            tag = data[0]
            data = data[1:]
            result = None

            for p in Packet.__subclasses__():
                if p.tag == tag:
                    result, data = p.parse(data)
                    break

            if result is not None:
                packets.append(result)
            else:
                logger.debug(f"Could not find a packet which can parse '{tag}'")
                logger.debug(
                    f"Available packets: "
                    f"{', '.join(p.__name__ for p in Packet.__subclasses__())}"
                )
                return []
        return packets

    def serialize(self, getID: callable) -> bytes:
        """
        Serializes the packet into bytes for sending to the server

        Args:
            getID (callable): Method to get the current reliable id
        """
        return self.data
