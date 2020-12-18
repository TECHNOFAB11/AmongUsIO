#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import Tuple
from .helpers import readPacked


class Task:
    id: int
    complete: bool

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple["Task", bytes]:
        task = cls()
        task.id, _data = readPacked(data)
        task.complete = bool(_data[0])
        return task, _data[1:]
