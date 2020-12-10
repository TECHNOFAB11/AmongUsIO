#!/usr/bin/python3
# -*- coding: utf-8 -*-
import struct
from typing import Union


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

    Example:
        unpack({"\x01\x01\x01\x01": "I", "\x01\x01": "h"})

    Args:
        data (dict): Dict with the values and data types, see example above
    """
    result = []
    for data, val in data.items():
        result.append(struct.unpack(val, data)[0])
    return result if len(result) > 1 else result[0]
