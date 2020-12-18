#!/usr/bin/python3
# -*- coding: utf-8 -*-
import struct
from typing import Union, Tuple


def formatHex(data: bytes) -> str:
    """
    Formats bytes into hex and more readable form
    """
    return " ".join(data.hex()[i : i + 2] for i in range(0, len(data.hex()), 2))


def pack(data: dict) -> bytes:
    """
    Packs multiple variables at once to bytes

    Example:
        pack({50: "I", 22: "h"})

    Args:
        data (dict): Dict with the values and data types, see example above
    """
    result = b""
    for data, val in data.items():
        result += struct.pack(val, data)
    return result


def unpack(data: dict) -> Union[list, int]:
    """
    Unpacks multiple variables at once to bytes
    If there is only one entry to unpack the result will be returned directly
    and not inside of a list

    Example:
        unpack({b"\x01\x01\x01\x01": "I", b"\x01\x01": "h"})

    Args:
        data (dict): Dict with the values and data types, see example above
    """
    result = []
    for data, val in data.items():
        result.append(struct.unpack(val, data)[0])
    return result if len(result) > 1 else result[0]


def createPacked(data: int) -> bytes:
    """
    Packs data (int) into bytes

    Example:
        createPacked(500) # --> b'\xf4\x03'

    Args:
        data (int): The number to pack into bytes
    """
    result = bytearray()
    while True:
        b = data & 0xFF
        if data >= 0x80:
            b |= 0x80

        result.append(b)
        data >>= 7
        if not data > 0:
            break
    return bytes(result)


def readPacked(data: bytes) -> Tuple[int, bytes]:
    """
    Reads/unpacks a packed number from data (bytes)

    Example:
        readPacked(b'\xf4\x03') # --> 500

    Args:
        data (bytes): The bytes to unpack

    Returns:
        Tuple of the number and the remaining bytes
    """
    position = 0
    shift = 0
    output = 0
    rest = b""

    while position >= 0:
        b = data[position]
        rest = data[position + 1 :]
        if b >= 0x80:
            position += 1
            b ^= 0x80
        else:
            position = -1

        output |= b << shift
        shift += 7

    return output, rest


def writeString(data: str):
    data = bytes(data.encode())
    return createPacked(len(data)) + data


def readString(data: bytes):
    length, _data = readPacked(data)
    return _data[:length].decode(), _data[length:]


def readMessage(data: bytes):
    length = unpack({data[0:2]: ">h"})
    tag = data[2]
    return tag, data[3 : length + 3], data[length + 3 :]
