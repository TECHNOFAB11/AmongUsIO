#!/usr/bin/python3
# -*- coding: utf-8 -*-
import amongus
from amongus.enums import PlayerAttributes

client = amongus.Client(
    name="Bot",
    color=PlayerAttributes.Color.Black,
    hat=PlayerAttributes.Hat.Geoff_Keighley_Mask,
    skin=PlayerAttributes.Skin.Astronaut,
    pet=PlayerAttributes.Pet.Robot,
)


@client.event
async def on_ready():
    print("Connected!")
    await client.join_lobby("ABCDEF")


client.run(region="EU")
# or, for a custom server:
client.run(custom_server="your.server.ip:port")  # port is optional, default is 22023
