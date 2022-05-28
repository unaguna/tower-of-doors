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


GAME_STATUS_FIELDS = (
    "status",
    "player_num",
    "turn_player",
    "timestamp",
)


class GameStatusRecord(
    namedtuple(
        "GameStatusRecord",
        GAME_STATUS_FIELDS,
    )
):
    status: str
    player_num: int | None
    turn_player: int | None
    timestamp: datetime

    @property
    def on_game(self) -> bool:
        return self.status == "ON_GAME"

    @property
    def on_someones_turn(self) -> bool:
        return self.on_game and self.turn_player > 0

    @property
    def on_interval_turn(self) -> bool:
        return self.on_game and self.turn_player == 0
