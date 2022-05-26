from collections import namedtuple
from datetime import datetime
from enum import Enum


class DoorStatus(Enum):
    CLOSED = 0
    OPEN = 1


class DoorLogRecord(
    namedtuple(
        "DoorLogRecord",
        (
            "door_id",
            "status",
            "timestamp",
            "reason",
        ),
    )
):
    door_id: str
    status: DoorStatus
    timestamp: datetime
    reason: str
