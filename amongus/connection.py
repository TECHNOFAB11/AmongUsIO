#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Dict

import asyncio_dgram

from .enums import (
    DisconnectReason,
    GameSettings,
    MatchMakingTag,
    PacketType,
    PlayerAttributes,
    RPCTag,
    SpawnTag,
)
from .eventbus import EventBus
from .exceptions import ConnectionException
from .game import Game, GameList
from .helpers import formatHex
from .packets import (
    AcknowledgePacket,
    CheckColorPacket,
    DisconnectPacket,
    GameDataPacket,
    GetGameListV2Packet,
    HelloPacket,
    JoinGamePacket,
    Packet,
    PingPacket,
    ReliablePacket,
    SendChatPacket,
    SetHatPacket,
    SetPetPacket,
    SetSkinPacket,
    SpawnPacket,
    UnreliablePacket,
)
from .packets.gamedata.base import GameDataToPacket
from .packets.gamedata.scenechange import SceneChangePacket
from .packets.rpc import RPCPacket
from .packets.rpc.checkname import CheckNamePacket
from .player import Player, PlayerList
from .queue import PacketQueue

logger = logging.getLogger(__name__)


class Connection:
    """
    Class for communication with the Among Us servers via UDP

    Attributes:
        socket: The UDP "socket" for UDP communication
        closed (bool): If the connection is closed
        connectTimeout (int): Timeout for connecting to server, default is 1000ms (1s)
        recvTimeout (int): Timeout for receiving messages, default is 10.000ms (10s)
        keepAliveTimeout (int): Timeout between ping messages
        host (str): current host
        port (int): current port
        lobby_code (str): current lobby_code
        region (str): current region
        result: The result which lets Client know why the connection was closed or
            similar, e.g. a wrong lobby code etc.
            Client returns this or raises this if it is an exception
    """

    socket = None
    closed: bool = False
    connectTimeout: int = 1000
    recvTimeout: int = 10000
    keepAliveTimeout: int = 1000
    name: str = None
    color: PlayerAttributes.Color
    hat: PlayerAttributes.Hat
    skin: PlayerAttributes.Skin
    pet: PlayerAttributes.Pet
    host: str = None
    port: int = None
    lobby_code: str = None
    region: str = None
    game_id: int = None
    host_id: int = None
    client_id: int = None
    net_id: int = None
    result = None
    game: Game
    eventbus: EventBus
    queue: PacketQueue
    players: PlayerList
    _id: int = 1
    _ready: asyncio.Event = asyncio.Event()
    _reader_task: asyncio.Task = None
    _pinger_task: asyncio.Task = None
    _ack_packets: Dict[int, Packet] = {}
    _player_amount: int = 0

    def __init__(self, eventbus: EventBus):
        self.eventbus = eventbus
        self.queue = PacketQueue()
        self.players = PlayerList()
        self.game = Game()

    @property
    def reliable_id(self) -> int:
        """
        This increases the current message id and returns the old value
        """
        _id = self._id
        self._id += 1
        return _id

    @property
    def ready(self) -> bool:
        """
        If we received a message from the server yet
        """
        return self._ready.is_set()

    async def connect(self, name: str, host: str, port: int = 22023) -> None:
        """
        Connects to the given server via UDP and starts listening for data on success

        Args:
            name (str): Name which will be displayed in Among Us
            host (str): Host/address of the server to connect to
            port (int): Port of the server to connect to, defaults to 22023

        Raises:
            Exception: Something went wrong, never happened while testing
        """
        self.host, self.port, self.name = host, port, name
        try:
            self.socket = await asyncio.wait_for(
                asyncio_dgram.connect((host, port)), timeout=self.connectTimeout / 1000
            )
        except asyncio.TimeoutError:
            logging.debug("Timeout when connecting to the server...")
            self.result = ConnectionException(
                f"Timeout connecting to {host}:{port}", DisconnectReason.Timeout
            )
            await self.disconnect(True)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info(f"Connected to {host}:{port} [{self.region}]")
            await self.send(
                HelloPacket.create(gameVersion=(2020, 11, 17), name=self.name)
            )
            self.closed = False
            self._reader_task = asyncio.create_task(self._reader())

    async def disconnect(self, force: bool, reconnect: bool = False) -> None:
        """
        Disconnects from the server

        Will do nothing if the connection is already closed

        Args:
            force (bool): Will just close the connection if True, otherwise it will
                inform the server first
            reconnect (bool): If we disconnect due to a reconnect, this prevents the
                closed attribute to be set, thus the client doesn't return
        """
        if self.closed:
            logger.debug("Not disconnecting, we're already closed!")
            return

        if not force and self._ready.is_set():
            logger.debug("Sending disconnect packet as were still connected")
            await self.send(DisconnectPacket.create())
        self.closed = not reconnect
        self.queue.clear()
        self._reader_task.cancel()
        self._pinger_task.cancel()
        self._ready.clear()
        self.socket.close()

    async def reconnect(self, host: str = None, port: int = None) -> None:
        """
        Disconnects and reconnects to the server because it sometimes doesn't send
        anything/doesn't answer in the first place

        If either host or port are given the last host/port will be overwritten and we
        will connect to the new server

        Args:
            host (str): Optional; The new host to connect to
            port (int): Optional; The new port to connect to
        """
        logger.debug("Reconnecting...")
        await self.disconnect(False, reconnect=True)
        host = host if host is not None else self.host
        port = port if port is not None else self.port
        logger.debug("Disconnected, now reconnecting...")
        await self.connect(self.name, host, port)

    async def wait_until_ready(self):
        await self._ready.wait()

    async def send(self, packet: Packet) -> None:
        """
        Serializes and sends a packet

        Args:
            packet: Packet; The packet to be sent
        """
        # we pass a lambda which returns the id because we dont know if the packet
        # needs the reliable id, so if it needs it and it gets called we increase the
        # id, else it just stays the same
        await self._send(packet.serialize(lambda: self.reliable_id))
        if packet.reliable:
            self._ack_packets[self._id - 1] = packet
        if packet.reliable and packet.tag not in [
            PacketType.Ping,
            PacketType.Acknowledgement,
        ]:
            await self._start_pinging(restart=True)
            # restart pinger as a reliable packet counts as a ping too?

    async def join_game(self, lobby_code: str) -> bool:
        """
        Sends a join game request to the server and returns True on success

        Args:
            lobby_code (str): The code for the game lobby

        Raises:
            ConnectionException: failed to join the game, see .reason for more
        """
        self.lobby_code = lobby_code
        logger.debug(f"Joining game '{lobby_code}'")
        await self.wait_until_ready()
        await self.send(ReliablePacket.create([JoinGamePacket.create(lobby_code)]))

        result = await self.queue.wait_for(
            lambda p: type(p.tag) == MatchMakingTag
            and p.tag in [MatchMakingTag.JoinedGame, MatchMakingTag.JoinGame]
        )

        if result.tag == MatchMakingTag.JoinGame:
            raise ConnectionException(
                "Joining game failed!",
                reason=DisconnectReason(result.values.reason),
                custom_reason=result.values.custom_reason,
            )
        elif result.tag == MatchMakingTag.JoinedGame:
            return True

    async def send_chat(self, message: str) -> None:
        """
        Sends a chat message to the server

        Args:
            message (str): The message to send
        """
        logger.debug(f"Sending chat message: {message}")
        await self.send(
            ReliablePacket.create(
                [
                    GameDataPacket.create(
                        [
                            RPCPacket.create(
                                [SendChatPacket.create(message)], net_id=self.net_id
                            )
                        ],
                        game_id=self.game_id,
                    )
                ]
            )
        )

    async def find_games(
        self, mapId: GameSettings.Map, impostors: int, language: GameSettings.Keywords
    ) -> GameList:
        """"""
        logger.debug(
            f"Finding games... Criteria: mapId={repr(mapId)}, impostors={impostors}, "
            f"language={repr(language)}"
        )
        await self.send(
            ReliablePacket.create(
                [
                    GetGameListV2Packet.create(
                        mapId=mapId, impostors=impostors, language=language
                    )
                ]
            )
        )
        result = await self.queue.wait_for(
            lambda p: type(p.tag) == MatchMakingTag
            and p.tag == MatchMakingTag.GetGameListV2
        )

        for game in result.values.games:

            async def _join_func():
                await self.join_game(game.readable_code)

            game.join = _join_func
        return GameList(
            games=result.values.games,
            skeld_count=result.values.skeld_count,
            mirahq_count=result.values.mirahq_count,
            polus_count=result.values.polus_count,
        )

    async def acknowledge(self, reliable_id: int) -> None:
        """
        Sends an Acknowledge message for the given id

        Args:
            reliable_id (int): The id of the message which should be acked
        """
        await self.send(AcknowledgePacket.create(reliable_id))

    async def on_packet(self, packet: Packet) -> None:
        """
        Called when a Packet has been received and parsed

        Args:
            packet (Packet): The received packet
        """
        if not self.ready:
            return

        if isinstance(packet, (ReliablePacket, UnreliablePacket)):
            logger.debug(
                f"Received "
                f"{'reliable' if isinstance(packet, ReliablePacket) else 'unreliable'} "
                f"packet, handling the contained packets:"
            )
            for p in packet:
                logger.debug(f" - {p}")
                await self.on_packet(p)
            return
        elif type(packet) == RPCPacket:
            logger.debug("Received RPC data, handling the contained packets...")
            for p in packet:
                await self.on_packet(p)
            return
        elif type(packet) == SpawnPacket:
            logger.debug("Received Spawn data, handling the contained packets...")
            for p in packet:
                await self.on_packet(p)
            return

        await self.queue.put(packet)

        if type(packet.tag) == PacketType:
            if packet.tag == PacketType.Disconnect:
                logger.debug("Server sent disconnect")
                self.result = ConnectionException(
                    "Server disconnected.",
                    packet.values.reason,
                    custom_reason=packet.values.custom_reason,
                )
                await self.disconnect(True)
                return
            elif packet.tag == PacketType.Acknowledgement:
                logger.debug(f"Got acknowledge for id={packet.values.reliable_id}")
                try:
                    p = self._ack_packets.pop(packet.values.reliable_id)
                except KeyError:
                    return
                else:
                    p.ack()
                return
            elif packet.tag == PacketType.Ping:
                logger.debug(f"Received ping number {packet.values.reliable_id}")
                return
        elif type(packet.tag) == MatchMakingTag:
            if packet.tag == MatchMakingTag.ReselectServer:
                logger.debug("Received ReselectServer, ignoring...")
                return
            elif packet.tag == MatchMakingTag.Redirect:
                logger.debug(
                    f"Received Redirect, now connecting to {packet.values.host}:"
                    f"{packet.values.port}"
                )
                await self.reconnect(packet.values.host, packet.values.port)
                return
            elif packet.tag == MatchMakingTag.JoinedGame:
                logger.info(f"Successfully joined game '{self.lobby_code}'!")
                self.eventbus.dispatch("game_join", self.lobby_code)
                self.game_id = packet.values.game_id
                self.client_id = packet.values.client_id
                self.host_id = packet.values.host_id
                return
            elif packet.tag in [MatchMakingTag.GameData, MatchMakingTag.GameDataTo]:
                if (
                    packet.tag == MatchMakingTag.GameDataTo
                    and packet.values.target != self.client_id
                ):
                    logger.debug("Received GameDataTo which is not for us")
                    return
                logger.debug("Received GameData, handling the contained packets...")
                for p in packet:
                    await self.on_packet(p)
                return
            elif packet.tag == MatchMakingTag.AlterGame:
                logger.debug(f"Received AlterGame: {packet}")
                self.game.public = packet.values.public
                return
            elif packet.tag == MatchMakingTag.GetGameListV2:
                # handled with queue.wait_for
                return
            elif packet.tag == MatchMakingTag.JoinGame:
                # handled with queue.wait_for
                return
        elif type(packet.tag) == RPCTag:
            if packet.tag == RPCTag.SetStartCounter:
                logger.debug(
                    "Received counter info, sending a SceneChange to get more data"
                )
                await self.send(
                    ReliablePacket.create(
                        [
                            GameDataPacket.create(
                                [SceneChangePacket.create(self.client_id)],
                                game_id=self.game_id,
                            )
                        ]
                    )
                )
                return
            elif packet.tag == RPCTag.SendChat:
                sender = packet.parent.values.net_id
                self.eventbus.dispatch(
                    "chat",
                    packet.values.message,
                    self.players.from_net_id(sender),
                )
                return
            elif packet.tag == RPCTag.SyncSettings:
                logger.debug("Received settings")
                packet.values.game.public = self.game.public
                self.game = packet.values.game
                self.eventbus.dispatch("game_settings", self.game)
                return
            elif packet.tag == RPCTag.UpdateGameData:
                logger.debug(f"Received UpdateGameData: {packet}")
                # i have no idea what this one is for, its just completely empty when i
                # tested it (only the player id is right, everything else is 0)
                return
            elif packet.tag == RPCTag.SetName:
                if packet.values.name is not None:
                    logger.debug(f"Got our name: {packet.values.name}")
                    self.name = packet.values.name
                    self.eventbus.dispatch("name_update", self.name)
                return
            elif packet.tag == RPCTag.SetColor:
                if PlayerAttributes.Color.has_value(packet.values.color):
                    logger.debug(f"Got color: {packet.values.color}")
                    self.color = PlayerAttributes.Color(packet.values.color)
                    self.eventbus.dispatch("color_update", self.color)
                return
        elif type(packet.tag) == SpawnTag:
            if packet.tag == SpawnTag.GameData:
                logger.debug(f"Received player data! {packet}")
                self._player_amount = packet.values.num_players
                self.players += packet.values.players
                if len(self.players) == self._player_amount:
                    self.eventbus.dispatch("player_data_update", list(self.players))
                return
            elif packet.tag == SpawnTag.PlayerControl:
                logger.debug(f"Received PlayerControl data: {packet}")
                if packet.parent.values.owner == self.client_id:
                    self.net_id = packet.values.net_id
                else:
                    player = self.players[packet.values.player_id]
                    if player is None:
                        player = Player()
                        player.id = packet.values.player_id
                        self.players += player
                    player.net_id = packet.values.net_id

                if self.players.complete() and self.net_id is not None:
                    await self.send(
                        ReliablePacket.create(
                            [
                                GameDataToPacket.create(
                                    [
                                        RPCPacket.create(
                                            [
                                                CheckNamePacket.create(name=self.name),
                                            ],
                                            net_id=self.net_id,
                                        ),
                                    ],
                                    game_id=self.game_id,
                                    target=self.host_id,
                                )
                            ]
                        )
                    )
                    await self.send(
                        ReliablePacket.create(
                            [
                                GameDataToPacket.create(
                                    [
                                        RPCPacket.create(
                                            [
                                                CheckColorPacket.create(
                                                    color=self.color
                                                ),
                                            ],
                                            net_id=self.net_id,
                                        ),
                                    ],
                                    game_id=self.game_id,
                                    target=self.host_id,
                                )
                            ]
                        )
                    )
                    await self.send(
                        ReliablePacket.create(
                            [
                                GameDataPacket.create(
                                    [
                                        RPCPacket.create(
                                            [
                                                SetPetPacket.create(pet=self.pet),
                                            ],
                                            net_id=self.net_id,
                                        ),
                                        RPCPacket.create(
                                            [
                                                SetHatPacket.create(hat=self.hat),
                                            ],
                                            net_id=self.net_id,
                                        ),
                                        RPCPacket.create(
                                            [
                                                SetSkinPacket.create(skin=self.skin),
                                            ],
                                            net_id=self.net_id,
                                        ),
                                    ],
                                    game_id=self.game_id,
                                )
                            ]
                        )
                    )
                return
        logger.warning(f"Unhandled packet: {packet}")

    async def _start_pinging(self, restart: bool = True) -> None:
        """
        Manages the _pinger, this method will start or restart it

        Args:
            restart (bool): If the current task should be cancelled before starting a
                new one
        """
        if not self.ready:
            return
        logger.debug("(Re)starting pinger...")
        if restart:
            self._pinger_task.cancel()
        self._pinger_task = asyncio.create_task(self._pinger())

    async def _pinger(self) -> None:
        """
        Periodically sends Ping packets
        """
        while not self.closed:
            await asyncio.sleep(self.keepAliveTimeout / 1000)
            await self.send(PingPacket.create(self.reliable_id))

    async def _send(self, payload: bytes) -> None:
        """
        Sends the data to the server

        Args:
            payload: bytes; the payload to send
        """
        logger.debug(f"Sending {len(payload)} bytes: {formatHex(payload)}")
        await self.socket.send(payload)

    async def _reader(self) -> None:
        """
        Reader loop which tries to receive bytes within the recvTimeout and lets the
        Connection reconnect on failure
        """
        while not self.closed:
            try:
                data, _ = await asyncio.wait_for(
                    self.socket.recv(), timeout=self.recvTimeout / 1000
                )
                asyncio.ensure_future(self._on_data(data))
            except asyncio.TimeoutError:
                if not self.closed:
                    logger.warning("Exceeded recvTimeout")
                    await self.reconnect()

    async def _on_data(self, data: bytes) -> None:
        """
        Called when raw data has been received

        Args:
            data (bytes): The payload which has been received
        """
        logger.debug(f"Received {len(data)} bytes: {formatHex(data)}")
        if not self._ready.is_set():
            self._ready.set()
            await self._start_pinging(restart=False)
            self.eventbus.dispatch("ready")
        packets = Packet.parse(data, first_call=True)
        for packet in packets:
            if packet.reliable and not isinstance(packet, AcknowledgePacket):
                await self.acknowledge(packet.reliable_id)
            await self.on_packet(packet)
