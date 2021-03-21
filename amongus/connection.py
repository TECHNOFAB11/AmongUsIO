#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import time
from typing import Dict, Tuple, Union

import asyncio_dgram

from .enums import (
    ChatNoteType,
    DataFlag,
    DisconnectReason,
    GameDataTag,
    GameSettings,
    MatchMakingTag,
    PacketType,
    PlayerAttributes,
    RPCTag,
    SpawnTag,
    TaskType,
)
from .eventbus import EventBus
from .exceptions import ConnectionException, SpectatorException
from .game import Game, GameList
from .helpers import dotdict, formatHex
from .packets import (
    AcknowledgePacket,
    CheckColorPacket,
    DataFlagPacket,
    DisconnectPacket,
    GameDataPacket,
    GetGameListV2Packet,
    HelloPacket,
    JoinGamePacket,
    MovementPacket,
    Packet,
    PingPacket,
    ReadyPacket,
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
from .task import Task

logger = logging.getLogger(__name__)


class Connection:
    """
    Class for communication with the Among Us servers via UDP

    Attributes:
        socket: The UDP "socket" for UDP communication
        latency (int): The latency of the connection in ms
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
    recvTimeout: int = 5000
    keepAliveTimeout: int = 1000
    name: str = None
    color: PlayerAttributes.Color
    hat: PlayerAttributes.Hat
    skin: PlayerAttributes.Skin
    pet: PlayerAttributes.Pet
    spectator: bool
    host: str = None
    port: int = None
    lobby_code: str = None
    region: str = None
    game_id: int = None
    host_id: int = None
    client_id: int = None
    net_ids: dotdict
    result = None
    game: Game
    eventbus: EventBus
    queue: PacketQueue
    players: PlayerList
    latency: int = float("inf")
    _sequence_ids: Dict[Player, int]
    _id: int = 1
    _ready: asyncio.Event = asyncio.Event()
    _reader_task: asyncio.Task = None
    _pinger_task: asyncio.Task = None
    _ack_packets: Dict[int, Packet] = {}
    _player_amount: int = 0
    _spectator_reconnected: bool = False
    _has_player_data: bool = False

    def __init__(self, eventbus: EventBus):
        """
        Init the connection with an eventbus for dispatching events, a message queue,
        a player list to handle the players and an empty Game object

        Args:
            eventbus (EventBus): The eventbus of the client, to be able to listen for
                events from the client/dispatching them directly here in this class
        """
        self.eventbus = eventbus
        self.queue = PacketQueue()
        self.players = PlayerList()
        self.game = Game()

    @property
    def reliable_id(self) -> int:
        """This increases the current message id and returns the old value"""
        _id = self._id
        self._id += 1
        return _id

    @property
    def ready(self) -> bool:
        """If we received a message from the server yet"""
        return self._ready.is_set()

    @property
    def player(self) -> Player:
        """The current player (/ourselves)"""
        return self.players.from_client_id(self.client_id)

    async def connect(self, name: str, host: str, port: int = 22023,
                      gameVersion: tuple = (2021, 3, 5)) -> None:
        """
        Connects to the given server via UDP and starts listening for data on success

        Args:
            name (str): Name which will be displayed in Among Us
            host (str): Host/address of the server to connect to
            port (int): Port of the server to connect to, defaults to 22023
            gameVersion: (tuple): The version of the game running on the server

        Raises:
            Exception: Something went wrong, never happened while testing
        """
        self._sequence_ids = {}
        self.net_ids = dotdict({})
        self.host, self.port, self.name, self.gameVersion = host, port, name, gameVersion
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
                HelloPacket.create(gameVersion=gameVersion, name=self.name)
            )
            self.closed = False
            self._reader_task = asyncio.create_task(self._reader())
            try:
                await asyncio.wait_for(
                    self.wait_until_ready(), timeout=self.recvTimeout / 1000
                )
            except asyncio.TimeoutError:
                self.result = ConnectionException(
                    "Timed out waiting for messages", DisconnectReason.Timeout
                )
                await self.disconnect(True)

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
        if self._reader_task is not None:
            self._reader_task.cancel()
        if self._pinger_task is not None:
            self._pinger_task.cancel()
        self._ready.clear()
        self.socket.close()

    async def reconnect(self, host: str = None, port: int = None, gameVersion: tuple = None) -> None:
        """
        Disconnects and reconnects to the server because it sometimes doesn't send
        anything/doesn't answer in the first place

        If either host or port are given the last host/port will be overwritten and we
        will connect to the new server

        Args:
            host (str): Optional; The new host to connect to
            port (int): Optional; The new port to connect to
            gameVersion (tuple): Optional: The version of the game running on the server
        """
        logger.debug("Reconnecting...")
        await self.disconnect(False, reconnect=True)
        host = host if host is not None else self.host
        port = port if port is not None else self.port
        gameVersion = gameVersion if gameVersion is not None else self.gameVersion
        logger.debug("Disconnected, now reconnecting...")
        await self.connect(self.name, host, port, gameVersion)

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
        if packet.reliable:

            async def _on_ack():
                self.latency = int(round((time.perf_counter() - _time_before) * 1000))
                if self.latency <= 0:
                    self.latency = 1

            packet.add_callback(_on_ack)
            _time_before = time.perf_counter()
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
        if self.spectator:
            raise SpectatorException("Chatting is not possible as spectator!")

        logger.debug(f"Sending chat message: {message}")
        await self.send(
            ReliablePacket.create(
                [
                    GameDataPacket.create(
                        [
                            RPCPacket.create(
                                [SendChatPacket.create(message)],
                                net_id=self.player.net_ids.control,
                            )
                        ],
                        game_id=self.game_id,
                    )
                ]
            )
        )

    async def find_games(
        self,
        mapId: GameSettings.SearchMap,
        impostors: int,
        language: GameSettings.Keywords,
    ) -> GameList:
        """
        Finds public games matching the passed properties

        Args:
            mapId (GameSettings.Map): The map
            impostors (int): The amount of impostors
            language (GameSettings.Keywords): The language of the chat
        """
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

    async def move(self, position: Tuple[int, int], velocity: Tuple[int, int]) -> None:
        """
        Moves the player to the given position

        Args:
            position (Tuple[int, int]): A tuple of x, y coordinates to move to
            velocity (Tuple[int, int]): A tuple of x, y coordinates with the
                velocity/relative position
        """
        if self.spectator:
            raise SpectatorException("Moving is not possible as spectator!")

        if self.player not in self._sequence_ids:
            self._sequence_ids[self.player] = 0
        else:
            self._sequence_ids[self.player] += 1

        await self.send(
            UnreliablePacket.create(
                [
                    GameDataPacket.create(
                        [
                            DataFlagPacket.create(
                                [
                                    MovementPacket.create(
                                        position=position,
                                        velocity=velocity,
                                        sequence_id=self._sequence_ids[self.player],
                                    )
                                ],
                                net_id=self.player.net_ids.network,
                            )
                        ],
                        game_id=self.game_id,
                    )
                ]
            )
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
            for p in packet:
                await self.on_packet(p)
            return
        elif type(packet) == RPCPacket:
            for p in packet:
                await self.on_packet(p)
            return
        elif type(packet) == SpawnPacket:
            for p in packet:
                await self.on_packet(p)
            return
        elif type(packet) == DataFlagPacket:
            if packet.values.net_id not in self.net_ids.keys():
                logger.warning(f"Net_id {packet.values.net_id} is not known?")
                return
            packet.parse_with_flag(self.net_ids[packet.values.net_id])
            for p in packet:
                await self.on_packet(p)
            return
        elif type(packet) in [GameDataPacket, GameDataToPacket]:
            if (
                packet.tag == MatchMakingTag.GameDataTo
                and packet.values.target != self.client_id
            ):
                logger.debug("Received GameDataTo which is not for us")
                return
            for p in packet:
                await self.on_packet(p)
            return

        await self.queue.put(packet)

        handlers = {
            PacketType: self.on_base_packet,
            MatchMakingTag: self.on_matchmaking_packet,
            GameDataTag: self.on_gamedata_packet,
            RPCTag: self.on_rpc_packet,
            SpawnTag: self.on_spawn_packet,
            DataFlag: self.on_dataflag_packet,
        }

        if not await handlers[type(packet.tag)](packet):
            logger.warning(
                f"Unhandled packet: {packet}. \nData: {formatHex(packet.data)}"
            )

    async def on_base_packet(self, packet: Packet):
        if packet.tag == PacketType.Disconnect:
            logger.debug("Server sent disconnect")
            self.result = ConnectionException(
                "Server disconnected.",
                packet.values.reason,
                custom_reason=packet.values.custom_reason,
            )
            await self.disconnect(True)
        elif packet.tag == PacketType.Acknowledgement:
            try:
                p = self._ack_packets.pop(packet.values.reliable_id)
            except KeyError:
                pass
            else:
                p.ack()
        elif packet.tag == PacketType.Ping:
            pass
        else:
            return False
        return True

    async def on_matchmaking_packet(self, packet: Packet) -> bool:
        if packet.tag == MatchMakingTag.ReselectServer:
            logger.debug("Received ReselectServer, ignoring...")
        elif packet.tag == MatchMakingTag.Redirect:
            logger.debug(
                f"Received Redirect, now connecting to {packet.values.host}:"
                f"{packet.values.port}"
            )
            await self.reconnect(packet.values.host, packet.values.port)
        elif packet.tag == MatchMakingTag.JoinedGame:
            logger.info(f"Successfully joined game '{self.lobby_code}'!")
            self.eventbus.dispatch("game_join", self.lobby_code)
            self.game_id = packet.values.game_id
            self.game.code = self.game_id
            self.client_id = packet.values.client_id
            self.host_id = packet.values.host_id

            if not self.spectator or not (
                self._spectator_reconnected or self._has_player_data
            ):
                logger.debug("Sending a SceneChange to get more data")
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
        elif packet.tag == MatchMakingTag.AlterGame:
            logger.debug(f"Received AlterGame: {packet}")
            self.game.public = packet.values.public
        elif packet.tag == MatchMakingTag.GetGameListV2:
            # handled with queue.wait_for
            pass
        elif packet.tag == MatchMakingTag.JoinGame:
            # handled with queue.wait_for
            pass
        elif packet.tag == MatchMakingTag.StartGame:
            if packet.values.game_id == self.game_id:
                await self.send(
                    ReliablePacket.create(
                        [
                            GameDataPacket.create(
                                [ReadyPacket.create(client_id=self.client_id)],
                                game_id=self.game_id,
                            )
                        ]
                    )
                )
                self.eventbus.dispatch("game_start", self.game)
            else:
                logger.warning("Received game start for the wrong game?")
        elif packet.tag == MatchMakingTag.EndGame:
            if packet.values.game_id == self.game_id:
                for player in self.players:
                    player.tasks.clear()
                # when the game ends we just need to send JoinGame again. Let the end
                # user decide if the client should reconnect to the lobby
                self.eventbus.dispatch("game_end", self.game, packet.values.reason)
            else:
                logger.warning("Received game end for the wrong game?")
        elif packet.tag == MatchMakingTag.RemovePlayer:
            if packet.values.game_id == self.game_id:
                player = self.players[packet.values.player_id]
                if player is not None:
                    self.players.remove(player)
                    new_host = self.players[packet.values.new_host_id]
                    new_host.host = True
                    self.eventbus.dispatch(
                        "player_remove", player, packet.values.reason
                    )
            else:
                logger.warning("Received player remove for the wrong game?")
        else:
            return False
        return True

    async def on_gamedata_packet(self, packet: Union[GameDataPacket, GameDataToPacket]):
        if packet.tag == GameDataTag.DespawnFlag:
            logger.debug(f"Received despawn flag for {packet.values.net_id}")
            del self.net_ids[packet.values.net_id]
            player = self.players.from_net_id(packet.values.net_id)
            if player is not None:
                self.players.remove(player)
                self.eventbus.dispatch("player_leave", player)
        elif packet.tag == GameDataTag.SceneChangeFlag:
            logger.debug("Someone else sent a scene change to get a spawn!")
            # no idea what to do with packet.values.client_id
        elif packet.tag == GameDataTag.ReadyFlag:
            logger.debug(f"Someone sent ready flag: {packet.values.client_id}")
        else:
            return False
        return True

    async def on_rpc_packet(self, packet: RPCPacket):
        if packet.tag == RPCTag.SetStartCounter:
            if packet.values.secondsleft < 0xFF:
                logger.debug(f"StartCounter update: {packet.values.secondsleft}s left")
                self.eventbus.dispatch("start_counter", packet.values.secondsleft)
        elif packet.tag == RPCTag.SendChat:
            sender = packet.parent.values.net_id
            self.eventbus.dispatch(
                "chat",
                packet.values.message,
                self.players.from_net_id(sender),
            )
        elif packet.tag == RPCTag.SyncSettings:
            logger.debug("Received settings")
            packet.values.game.public = self.game.public
            self.game = packet.values.game
            self.eventbus.dispatch("game_settings", self.game)
        elif packet.tag == RPCTag.UpdateGameData:
            if not self._spectator_reconnected:
                return True
            logger.debug(f"Received UpdateGameData: {packet}")
            self.players += packet.values.players
            self.eventbus.dispatch("players_update", self.players)
        elif packet.tag in [
            RPCTag.SetName,
            RPCTag.SetHat,
            RPCTag.SetPet,
            RPCTag.SetColor,
            RPCTag.SetSkin,
        ]:
            validators = {
                "name": lambda n: n is not None,
                "color": PlayerAttributes.Color.has_value,
                "hat": PlayerAttributes.Hat.has_value,
                "pet": PlayerAttributes.Pet.has_value,
                "skin": PlayerAttributes.Skin.has_value,
            }
            converters = {
                "color": PlayerAttributes.Color,
                "hat": PlayerAttributes.Hat,
                "pet": PlayerAttributes.Pet,
                "skin": PlayerAttributes.Skin,
            }
            # as these packets only have one value either way we just use that
            cosmetic = list(packet.values)[0]
            value = packet.values[cosmetic]
            logger.debug(f"Received Set{cosmetic}")

            if value is not None and validators[cosmetic](value):
                # valid
                if cosmetic in converters.keys():
                    # convert to enum
                    value = converters[cosmetic](value)

                if packet.parent.values.net_id in self.player.net_ids.values():
                    # for us
                    if getattr(self, cosmetic) != value:
                        setattr(self, cosmetic, value)
                        kwargs = {cosmetic: value}
                        self.eventbus.dispatch("attribute_update", **kwargs)
                else:
                    player = self.players.from_net_id(packet.parent.values.net_id)
                    if player is not None and getattr(player, cosmetic) != value:
                        setattr(player, cosmetic, value)
                        self.eventbus.dispatch("player_update", player)
        elif packet.tag == RPCTag.SetInfected:
            for _id in packet.values.impostor_ids:
                player = self.players[_id]
                if player is not None:
                    player.impostor = True
                    self.eventbus.dispatch("player_update", player)
        elif packet.tag == RPCTag.MurderPlayer:
            impostor = self.players.from_net_id(packet.parent.values.net_id)
            victim = self.players.from_net_id(packet.values.target)
            if victim is None and packet.values.target in self.player.net_ids.values():
                # we're the victim... rip
                logger.debug(f"{impostor.name} killed us!")
                self.eventbus.dispatch("death", impostor)
            else:
                victim.statusBitField |= 4
                victim.death_position = victim.position
                logger.debug(f"{impostor.name} killed {victim.name}")
                self.eventbus.dispatch("player_kill", impostor, victim)
        elif packet.tag == RPCTag.ReportDeadBody:
            player = self.players.from_net_id(packet.parent.values.net_id)
            if packet.values.player_id == 0xFF:
                # emergency button
                self.eventbus.dispatch("button_press", player)
            else:
                # dead body reported
                victim = self.players[packet.values.player_id]
                self.eventbus.dispatch("body_report", player, victim)
        elif packet.tag == RPCTag.StartMeeting:
            player = self.players[packet.values.player_id]
            self.eventbus.dispatch("meeting_start", player)
        elif packet.tag == RPCTag.VotingComplete:
            args = [None]
            if packet.values.player_id < 0xFF:
                args = [self.players[packet.values.player_id]]
            self.eventbus.dispatch("voting_end", *args)
        elif packet.tag == RPCTag.Close:
            self.eventbus.dispatch("meeting_stop")
        elif packet.tag == RPCTag.EnterVent:
            impostor = self.players[packet.values.player_id]
            self.eventbus.dispatch("vent_enter", impostor)
        elif packet.tag == RPCTag.ExitVent:
            impostor = self.players[packet.values.player_id]
            self.eventbus.dispatch("vent_exit", impostor)
        elif packet.tag == RPCTag.SetTasks:
            player = self.players[packet.values.player_id]
            if player is not None:
                for task_id in packet.values.task_ids:
                    if TaskType.has_value(task_id):
                        player.tasks.append(Task(id=task_id))
                self.eventbus.dispatch("player_tasks_update", player)
            else:
                logger.warning(
                    f"Received SetTasks for unknown player id: "
                    f"{packet.values.player_id}"
                )
        elif packet.tag == RPCTag.SnapTo:
            player = self.players.from_net_id(packet.parent.values.net_id)
            player.position = packet.values.position
            self.eventbus.dispatch("vent_move", player)
        elif packet.tag == RPCTag.SendChatNote:
            player = self.players[packet.values.player_id]
            if ChatNoteType.has_value(packet.values.note_type):
                if packet.values.note_type == ChatNoteType.DidVote:
                    self.eventbus.dispatch("player_vote", player)
            else:
                logger.warning("Unknown ChatNoteType")
        else:
            return False
        return True

    async def on_spawn_packet(self, packet: SpawnPacket):
        if packet.tag == SpawnTag.GameData:
            logger.debug(f"Received player data! {packet}")
            self._player_amount = packet.values.num_players
            self.players += packet.values.players
        elif packet.tag == SpawnTag.PlayerControl:
            logger.debug(f"Received PlayerControl data: {packet}")
            for key, net_id in packet.values.net_ids.items():
                _translate = {
                    "control": DataFlag.Control,
                    "physics": DataFlag.Physics,
                    "network": DataFlag.Network,
                }
                self.net_ids[net_id] = _translate[key]

            player = self.players[packet.values.player_id]
            if player is None:
                player = Player()
                player.id = packet.values.player_id
                self.players += player
            player.client_id = packet.parent.values.owner
            player.net_ids = packet.values.net_ids

            if player.client_id == self.host_id:
                player.host = True

            if self.players.complete():
                self.eventbus.dispatch("players_update", list(self.players))

            if self.player is not None and all(
                n is not None for n in self.player.net_ids.values()
            ):
                if self.spectator:
                    if (
                        not (self._has_player_data and self._spectator_reconnected)
                        and self.players.complete()
                    ):
                        self._has_player_data = True
                        await self.reconnect()
                        self._spectator_reconnected = True
                else:
                    await self.send(
                        ReliablePacket.create(
                            [
                                GameDataToPacket.create(
                                    [
                                        RPCPacket.create(
                                            [
                                                CheckNamePacket.create(name=self.name),
                                            ],
                                            net_id=self.player.net_ids.control,
                                        ),
                                    ],
                                    game_id=self.game_id,
                                    target=self.host_id,
                                )
                            ]
                        )
                    )
                    await self.update_player_attributes()
        else:
            return False
        return True

    async def on_dataflag_packet(self, packet: DataFlagPacket):
        if packet.tag == DataFlag.Network:
            # movement
            player = self.players.from_net_id(packet.parent.values.net_id)
            if player is None:
                logger.warning(f"Received movement data for unknown player! {packet}")
                return True
            if packet.values.sequence_id > self._sequence_ids.get(player, 0):
                self._sequence_ids[player] = packet.values.sequence_id
                player.position = packet.values.position
                player.velocity = packet.values.velocity
                self.eventbus.dispatch("player_move", player)
            else:
                logger.debug(
                    f"Got old movement packet with sequence "
                    f"id {packet.values.sequence_id}"
                )
        else:
            return False
        return True

    async def update_player_attributes(self):
        """Updates the player attributes like skin, pet, color etc."""
        await self.send(
            ReliablePacket.create(
                [
                    GameDataToPacket.create(
                        [
                            RPCPacket.create(
                                [
                                    CheckColorPacket.create(color=self.color),
                                ],
                                net_id=self.player.net_ids.control,
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
                                net_id=self.player.net_ids.control,
                            ),
                            RPCPacket.create(
                                [
                                    SetHatPacket.create(hat=self.hat),
                                ],
                                net_id=self.player.net_ids.control,
                            ),
                            RPCPacket.create(
                                [
                                    SetSkinPacket.create(skin=self.skin),
                                ],
                                net_id=self.player.net_ids.control,
                            ),
                        ],
                        game_id=self.game_id,
                    )
                ]
            )
        )

    async def _start_pinging(self, restart: bool = True) -> None:
        """
        Manages the _pinger, this method will start or restart it

        Args:
            restart (bool): If the current task should be cancelled before starting a
                new one
        """
        if not self.ready:
            return
        if restart:
            self._pinger_task.cancel()
        self._pinger_task = asyncio.create_task(self._pinger())

    async def _pinger(self) -> None:
        """Periodically sends Ping packets"""
        while not self.closed:
            await asyncio.sleep(self.keepAliveTimeout / 1000)
            await self.send(PingPacket.create(self.reliable_id))

    async def _send(self, payload: bytes) -> None:
        """
        Sends the data to the server

        Args:
            payload: bytes; the payload to send
        """
        if asyncio.get_event_loop().get_debug():
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
        if asyncio.get_event_loop().get_debug():
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
