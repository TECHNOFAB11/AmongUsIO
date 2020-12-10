#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import amongus
from amongus.enums import DisconnectReason

# enable debug logging for debugging
logging.basicConfig(format='Linie:%(lineno)4d %(name)-26s %(levelname)-8s: %(message)s', level=logging.DEBUG)

client = amongus.Client(name="Bot")

try:
    client.run(region="EU")
except amongus.ConnectionError as e:
    if e.reason == DisconnectReason.IncorrectVersion:
        print("wrong version!")
    elif e.reason == DisconnectReason.Custom:
        print("disconnected because: ", e.custom_reason)
    else:
        print("disconnect reason: ", repr(e.reason))
