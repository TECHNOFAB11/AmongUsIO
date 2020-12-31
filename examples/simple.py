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
async def on_chat(message: str, sender: amongus.Player):
    print(f"[Chat] {sender.name}: {message}")

    if message == "stop":
        await client.stop()
    elif message == "source":
        await client.send_chat("https://gitlab.com/TECHNOFAB/AmongUsIO")
    elif message == "ping":
        await client.send_chat(f"Pong! Latency: {client.latency}ms")
    else:
        # echo back
        await client.send_chat(message)


client.run(region="EU")
# or, for a custom server:
client.run(custom_server="your.server.ip:port")  # port is optional, default is 22023
