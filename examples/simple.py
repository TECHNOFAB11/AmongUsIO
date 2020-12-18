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


client.run(region="EU")
