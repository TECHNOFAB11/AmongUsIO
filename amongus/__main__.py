#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from .packets.base import Packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--parse",
        help="Parse bytes and return the packets contained, used for "
        "parsing data from Wireshark for example",
    )
    args = parser.parse_args()

    if args.parse is not None:
        data: bytes = bytes.fromhex(args.parse)
        print(Packet.parse(data))  # noqa: T001
