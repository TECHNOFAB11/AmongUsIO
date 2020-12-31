#!/usr/bin/python3
# -*- coding: utf-8 -*-
import amongus

client = amongus.Client(name="Bot", spectator=True)
# we can still receive all kinds of things other players do, like movement, chatting,
# maybe even killing. But as were in a state between existing and not we cannot send
# any commands to control our "player" (which is invisible/non-existent)


@client.event
async def on_ready():
    print("Connected!")
    await client.join_lobby("ABCDEF")


@client.event
async def on_game_join(lobby_code: str):
    print(f"Joined game lobby '{lobby_code}'")


@client.event
async def on_chat(message: str, sender: amongus.Player):
    print(f"[Chat] {sender.name}: {message}")
    # as were in spectator mode we cant answer, only read/receive
    # if you still wanna try chatting you'll be greeted by a SpectatorException :)
    await client.send_chat(message)


client.run(region="EU")
# or, for a custom server:
client.run(custom_server="your.server.ip:port")  # port is optional, default is 22023
# !!! The only custom server i know of is Impostor, which does NOT support spectating !!!
