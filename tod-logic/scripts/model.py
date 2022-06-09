from collections import namedtuple
from datetime import datetime
from enum import Enum


class GameStatus(Enum):
    """State of game and the tower"""

    MAINTENANCE = "MAINTENANCE"
    STANDBY = "STANDBY"
    ON_GAME = "ON_GAME"


class DoorStatus(Enum):
    """State of door opening"""

    CLOSED = 0
    OPEN = 1


class YawingStatus(Enum):
    """State of tower yawing"""

    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"
    ON_YAWING = "ON_YAWING"
    COMPLETED = "COMPLETED"


class YawingReason(Enum):
    """Reason of tower yawing"""

    GAME_PHASE = "GAME_PHASE"
    REMOTE = "REMOTE"


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
    """The record of `door_log`"""

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
    """The record of `game_status`"""

    status: GameStatus
    player_num: int | None
    turn_player: int | None
    timestamp: datetime

    @property
    def on_game(self) -> bool:
        """If true, it is the record created in the middle of a game"""
        return self.status == GameStatus.ON_GAME

    @property
    def on_maintenance(self) -> bool:
        """If true, it is the record created in maintenance"""
        return self.status == GameStatus.MAINTENANCE

    @property
    def on_someones_turn(self) -> bool:
        """If true, it is the record created in user's phase of a game"""
        return self.on_game and self.turn_player > 0

    @property
    def on_interval_turn(self) -> bool:
        """If true, it is the record created in interval phase of a game"""
        return self.on_game and self.turn_player == 0


YAWING_SCHEDULE_FIELDS = (
    "id",
    "aim_azimuth",
    "yawing_reason",
    "schedule_start_time",
    "schedule_end_time",
    "yawing_status",
    "actual_start_time",
    "actual_end_time",
)


class YawingScheduleRecord(
    namedtuple(
        "YawingScheduleRecord",
        YAWING_SCHEDULE_FIELDS,
    )
):
    """The record of `yawing_schedule`"""

    id: int
    aim_azimuth: float
    yawing_reason: YawingReason
    schedule_start_time: datetime
    schedule_end_time: datetime
    yawing_status: YawingStatus
    actual_start_time: datetime | None
    actual_end_time: datetime | None
