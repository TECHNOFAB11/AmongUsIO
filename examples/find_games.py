#!/usr/bin/python3
# -*- coding: utf-8 -*-
import amongus

client = amongus.Client(name="Bot")


@client.event
async def on_ready():
    print("Connected!")
    result = await client.find_games(
        impostors=2
    )  # filter by impostors, map and language
    print(
        f"There are "
        f"{sum([result.skeld_count, result.mirahq_count, result.polus_count])} games."
    )
    print(f"Found games: {result.games}")

    if len(result.games) > 0:
        # join the first lobby we can find
        await result.games[0].join()


@client.event
async def on_game_join(lobby_code: str):
    print(f"Joined game lobby '{lobby_code}'")


@client.event
async def on_chat(message: str, sender: amongus.Player):
    print(f"[Chat] {sender.name}: {message}")


client.run(region="EU")
# or, for a custom server:
client.run(custom_server="your.server.ip:port")  # port is optional, default is 22023
