#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Coroutine, List

from ..enums import PacketType
from ..helpers import formatHex

logger = logging.getLogger(__name__)


class dotdict(dict):
    """
    Custom dict with which the items can be accessed like an attribute

    Example:
        .. code-block:: python

           d = dotdict({"something":5})
           d.something  # --> 5
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Packet:
    """"""

    parent: "Packet" = None
    data: bytes
    tag: int
    values: dotdict
    reliable_id: int
    callback: callable
    _contained_packets: list

    def __init__(
        self, data: bytes, tag: int = None, contained_packets: list = None, **kwargs
    ):
        self.data = data
        self.tag = self.tag or tag
        self.parent = self.parent or None
        self.values = dotdict(kwargs)
        self.contained_packets = [] if contained_packets is None else contained_packets
        self.callback = None

    def __iter__(self):
        return iter(self.contained_packets)

    def __repr__(self):
        ignore = ["tag", "_contained_packets", "data"]
        items = []
        for item in dir(self):
            val = getattr(self, item)
            if not callable(val) and not item.startswith("__") and item not in ignore:
                items.append(f"{item}={val}")
        return f"<{self.__class__.__name__} {', '.join(items)}>"

    @property
    def reliable(self):
        return self.__class__.__name__ in [
            "PingPacket",
            "ReliablePacket",
            "AcknowledgePacket",
            "HelloPacket",
        ]

    @property
    def contained_packets(self):
        return self._contained_packets

    @contained_packets.setter
    def contained_packets(self, value):
        self._contained_packets = value
        for packet in self._contained_packets:
            packet.parent = self

    def add_packet(self, packet: "Packet"):
        """
        Adds a packet to the contained_packets

        Args:
            packet (Packet): The packet to add
        """
        packet.parent = self
        self._contained_packets.append(packet)

    def add_callback(self, cb: Coroutine):
        """
        Sets the callback which gets run when the packet was acknowledged

        Args:
            cb (Coroutine): A coroutine
        """
        self.callback = cb

    def ack(self) -> None:
        """
        Runs the acknowledge callback
        """
        if self.callback is None:
            return
        asyncio.ensure_future(self.callback())

    @classmethod
    def create(cls, *args, **kwargs) -> "Packet":
        """
        Returns a packet with its unique values

        Every subclass has to overwrite this to be able to use the data passed
        depending on its use case and function
        """
        raise NotImplementedError

    @staticmethod
    def parse(data: bytes, first_call=False) -> List["Packet"]:
        """
        Parses bytes and returns the contained packets

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
                if first_call and type(p.tag) != PacketType:
                    continue
                if p.tag == tag or (type(p.tag) == list and tag in p.tag):
                    result, data = p.parse(data)
                    break

            if result is not None:
                packets.append(result)
            else:
                logger.debug(f"Could not find a packet which can parse '{tag}'")
                logger.debug(f"Data: {formatHex(data)}")
                data = b""
            first_call = False
        return packets

    def serialize(self, getID: callable) -> bytes:
        """
        Serializes the packet into bytes for sending to the server

        Args:
            getID (callable): Method to get the current reliable id
        """
        return self.data
