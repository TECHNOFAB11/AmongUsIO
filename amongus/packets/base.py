#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from typing import List
from amongus.enums import PacketType

logger = logging.getLogger(__name__)


class dotdict(dict):
    """
    Custom dict with which the items can be accessed like an attribute

    Example:
        d = dotdict({"something":5})
        d.something  # --> 5
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Packet:
    """

    """

    data: bytes
    tag: int
    contained_packets: list
    values: dotdict
    reliable_id: int

    def __init__(
        self, data: bytes, tag: int = None, contained_packets: list = None, **kwargs
    ):
        self.data = data
        if tag is not None:
            self.tag = tag
        self.values = dotdict(kwargs)
        self.contained_packets = contained_packets or []

    def __iter__(self):
        return iter(self.contained_packets)

    def __repr__(self):
        ignore = ["tag"]
        items = []
        for item in dir(self):
            val = getattr(self, item)
            if not callable(val) and not item.startswith("__") and item not in ignore:
                items.append(f"{item}={val}")
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
        """

        """
        raise NotImplementedError

    @staticmethod
    def parse(data: bytes, first_call=False) -> List["Packet"]:
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
                if type(p.tag) == PacketType and not first_call:
                    # when its a "parent"/"main"/whatever packet require first_call to
                    # be True. This ensures that packets like Reliable can be parsed
                    # but at the same time packets like JoinGame work like intended
                    continue
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
