#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Coroutine, List

from ..enums import PacketType
from ..helpers import dotdict, formatHex

logger = logging.getLogger(__name__)


class Packet:

    """The base class for all packets sent and received by this library

    Attributes:
        parent (Packet): The parent packet if applicable
        data (bytes): The raw data of the packet, only rarely if ever used
        tag (int): The tag of the packet, should be overwritten by all subclasses
        values (dotdict): The values of the packet.
            :meth:`deserialize` and :meth:`__init__` will add values and
            :meth:`serialize` will then use these and serialize them in the right format
        reliable_id (int): If its a reliable packet this will contain the reliable id
        callback (Coroutine): A coroutine which gets called when the packet was acked
            by the server
        contained_packets (list): The sub-packets of this packet, as packets
            are nearly always nested
        reliable (bool): If the packet is reliable
    """

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
        """
        Initializes the packet, do not overwrite this!
        To create a packet use :meth:`Packet.create` instead

        Args:
            data (bytes): The raw data which resulted in this packet when parsed
            contained_packets (list): The child packets nested inside of this one
        """
        self.data = data
        self.tag = self.tag if self.tag is not None else tag
        self.parent = self.parent or None
        self.values = dotdict(kwargs)
        self.contained_packets = [] if contained_packets is None else contained_packets
        self.callback = None

    def __iter__(self):
        """Makes it possible to iterate over the contained packets."""
        return iter(self.contained_packets)

    def __repr__(self):
        """
        Goes through all attributes and displays them if they're not callable or
        builtins starting with '__'

        By adding attributes to the `ignore` list you can prevent them from being shown
        """
        ignore = ["tag", "_contained_packets", "data"]
        items = []
        for item in dir(self):
            val = getattr(self, item)
            if not callable(val) and not item.startswith("__") and item not in ignore:
                if item == "parent":
                    items.append(f"{item}={val.__class__.__name__}")
                else:
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
