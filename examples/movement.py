#!/usr/bin/python3
# -*- coding: utf-8 -*-
import amongus

client = amongus.Client(name="Bot")


@client.event
async def on_ready():
    print("Connected!")
    await client.join_lobby("ABCDEF")


@client.event
async def on_game_join(lobby_code: str):
    print(f"Joined game lobby '{lobby_code}'")


@client.event
async def on_player_move(player: amongus.Player):
    print("Player moved, following:", player.name)
    # follows the player that is currently moving (this teleports, probably banned in
    # the future thru anti cheat?)
    await client.move(player.position, player.velocity)


client.run(region="EU")
# or, for a custom server:
client.run(custom_server="your.server.ip:port")  # port is optional, default is 22023
