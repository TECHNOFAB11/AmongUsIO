#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from ...enums import DisconnectReason, MatchMakingTag
from ...helpers import unpack
from ...packets import Packet


class RemovePlayerPacket(Packet):
    tag = MatchMakingTag.RemovePlayer

    @classmethod
    def create(cls, *args, **kwargs) -> "RemovePlayerPacket":
        raise NotImplementedError

    @classmethod
    def parse(cls, data: bytes) -> Tuple["RemovePlayerPacket", bytes]:
        game_id = unpack({data[0:4]: "I"})
        player_id = unpack({data[4:8]: "I"})
        new_host_id = unpack({data[8:12]: "I"})
        reason = data[12]
        if DisconnectReason.has_value(reason):
            reason = DisconnectReason(reason)
        return (
            cls(
                data,
                game_id=game_id,
                player_id=player_id,
                new_host_id=new_host_id,
                reason=reason,
            ),
            b"",
        )

    def serialize(self, getID: callable) -> bytes:
        raise NotImplementedError
