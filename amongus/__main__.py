#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from typing import Union

from amongus.helpers import formatHex

from .packets.base import Packet


def print_children(p: Union[Packet, list], depth: int, with_data: bool = False):
    for child in p:
        print(f"{'   '*depth}{child.__class__.__name__}: {child.values}")  # noqa: T001
        if with_data:
            print(f"{'   '*depth}---> {formatHex(child.data)}")  # noqa: T001
        if len(child.contained_packets) > 0:
            print_children(child, depth=depth + 1, with_data=with_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--parse",
        help="Parse bytes and return the packets contained, used for "
        "parsing data from Wireshark for example",
    )
    parser.add_argument(
        "--with-data",
        type=bool,
        default=False,
        help="When parsing, print the respective data of each packet aswell",
    )
    args = parser.parse_args()

    if args.parse is not None:
        data: bytes = bytes.fromhex(args.parse.replace(" ", ""))
        packets = Packet.parse(data, first_call=True)
        print_children(packets, depth=0, with_data=bool(args.with_data))
