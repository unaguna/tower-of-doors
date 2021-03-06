from dataclasses import asdict, dataclass
import dataclasses
from datetime import datetime, timedelta
from enum import Enum
from typing import Sequence


class GameEndReason(Enum):
    """Reason of game end"""

    REMOTE = "REMOTE"
    MAINTENANCE = "MAINTENANCE"
    MASTER_KEY = "MASTER_KEY"

    @classmethod
    def or_none(cls, name: str | None) -> "GameEndReason":
        return GameEndReason(name) if name is not None else None


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


@dataclass(order=False, kw_only=True)
class DoorLogRecord:
    """The record of `door_log`"""

    door_id: str
    status: DoorStatus
    timestamp: datetime
    reason: str


@dataclass(order=False, kw_only=True)
class GameModel:
    """The model of `game`"""

    player_num: int
    interval_period: timedelta
    player_period: timedelta
    start_time: datetime
    end_time: datetime | None = None
    game_end_reason: GameEndReason | None = None


@dataclass(order=False, kw_only=True)
class GameRecord(GameModel):
    """The record of `game`"""

    id: int

    @classmethod
    def of(cls, model: GameModel, id: int) -> "GameRecord":
        return GameRecord(id=id, **asdict(model))

    @classmethod
    def fields(cls) -> Sequence[str]:
        return tuple(f.name for f in dataclasses.fields(cls))


@dataclass(order=False, kw_only=True)
class GameStatusRecord:
    """The record of `game_status`"""

    status: GameStatus
    game_id: int | None
    turn_player: int | None
    timestamp: datetime

    @classmethod
    def fields(cls) -> Sequence[str]:
        return tuple(f.name for f in dataclasses.fields(cls))

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


@dataclass(order=False, kw_only=True)
class YawingScheduleModel:
    """The model of `yawing_schedule`"""

    aim_azimuth: float
    yawing_reason: YawingReason
    schedule_start_time: datetime
    schedule_end_time: datetime
    yawing_status: YawingStatus
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None


@dataclass(order=False, kw_only=True)
class YawingScheduleRecord(YawingScheduleModel):
    """The record of `yawing_schedule`"""

    id: int

    @classmethod
    def of(cls, model: YawingScheduleModel, id: int) -> "YawingScheduleRecord":
        return YawingScheduleRecord(id=id, **asdict(model))

    @classmethod
    def fields(cls) -> Sequence[str]:
        return tuple(f.name for f in dataclasses.fields(cls))
