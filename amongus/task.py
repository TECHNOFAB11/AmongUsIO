#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple

from .enums import TaskType
from .helpers import readPacked


class Task:
    id: int  # noqa: A003
    complete: bool

    def __init__(self, id: int, complete: bool = False):  # noqa: A002
        self.id = id
        self.complete = complete

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple["Task", bytes]:
        _id, _data = readPacked(data)
        return cls(id=_id, complete=bool(_data[0])), _data[1:]

    @property
    def type(self) -> TaskType:  # noqa: A003
        return TaskType(self.id)
