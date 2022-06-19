from datetime import datetime, timedelta

import MySQLdb

import logic.azimuth
from model import GameEndReason, GameRecord, GameStatusRecord
import service
import service.azimuthlog
import service.doorlog
import service.doorstatus
import service.game
import service.gamestatus
import service.yawingschedule


INTERVAL_PERIOD_SEC = 300
PLAYER_PERIOD_SEC = 300


def start_game(
    player_num: int,
    *,
    interval_period: timedelta = None,
    player_period: timedelta = None,
):
    """Start a game

    Args:
        player_num (int):
            Number of groups of players participating in the game.
    """
    if interval_period is None:
        interval_period = timedelta(seconds=INTERVAL_PERIOD_SEC)
    if player_period is None:
        player_period = timedelta(seconds=PLAYER_PERIOD_SEC)

    now = datetime.now()
    with service.connect() as connection:
        game_record = service.game.insert_start_game(
            connection=connection,
            start_time=now,
            player_num=player_num,
            interval_period=interval_period,
            player_period=player_period,
        )

        service.gamestatus.insert_start_game(
            connection=connection, game_id=game_record.id, now=now
        )
        # TODO: start yawing because the game will start with interval-turn
        connection.commit()


def end_game(game_end_reason: GameEndReason):
    """Terminate a game"""
    now = datetime.now()
    with service.connect() as connection:
        current_game_status = service.gamestatus.get_latest(connection=connection)
        service.gamestatus.insert_end_game(
            current_game_status=current_game_status, now=now, connection=connection
        )
        service.game.update_end_game(
            current_game_status.game_id,
            game_end_reason,
            end_time=now,
            connection=connection,
        )

        connection.commit()


def make_turn_next(
    now: datetime,
    *,
    connection: MySQLdb.Connection = None,
    current_game_status: GameStatusRecord = None,
    current_game: GameRecord = None,
):
    """Progressing game phases

    Execution of this function will move to the next phase regardless of the time remaining.
    If you want to move to the next phase only when there is no time remaining,
    use `make_turn_next_with_judge()`.

    Args:
        now (datetime):
            current time
        connection (MySQLdb.Connection, optional):
            Connection to DB.
            If not specified, a new connection is created and committed
            when the job of this function is successfully completed.
        current_game_status (GameStatusRecord, optional):
            Current game state.
            If not specified, retrieve from DB.
        current_game (GameRecord, optional):
            Current game.
            If not specified, retrieve from DB.
    """
    if connection is None:
        with service.connect() as new_connection:
            make_turn_next(
                now=now,
                connection=new_connection,
                current_game_status=current_game_status,
                current_game=current_game,
            )
            new_connection.commit()
        return

    if current_game_status is None:
        current_game_status = service.gamestatus.get_latest(connection=connection)

    if current_game is None:
        current_game = service.game.get_by_id(
            id=current_game_status.game_id, connection=connection
        )

    # Move turn next
    next_game_status = service.gamestatus.insert_next_turn_of(
        current_game_status, current_game.player_num, connection=connection
    )

    # Close doors
    closed_doors = service.doorstatus.get_opened_door_id_list(connection=connection)
    for door_id in closed_doors:
        service.doorlog.insert_close(door_id, connection=connection)

    # schedule yawing
    if next_game_status.on_interval_turn:
        schedule_end_time = now + (current_game.interval_period) * 4 / 5
        scheduled_yawing = logic.azimuth.schedule_yaw(
            yawing_angle=60.0,
            schedule_start_time=now,
            schedule_end_time=schedule_end_time,
            connection=connection,
        )
    else:
        scheduled_yawing = None

    # log
    print("increased turn to", next_game_status)
    if len(closed_doors) > 0:
        print("closed doors:", closed_doors)
    if scheduled_yawing is not None:
        print("yawing scheduled:", scheduled_yawing)


def make_turn_next_with_judge(now: datetime):
    """Progressing game phases if there is no time remaining.

    Args:
        now (datetime):
            current time
    """
    with service.connect() as connection:
        game_status = service.gamestatus.get_latest(connection=connection)

        if not game_status.on_game:
            return

        game = service.game.get_by_id(game_status.game_id, connection=connection)
        game_status_oldness = now - game_status.timestamp

        if (
            game_status.on_interval_turn and game_status_oldness >= game.interval_period
        ) or (
            game_status.on_someones_turn and game_status_oldness >= game.player_period
        ):
            make_turn_next(
                now=now,
                connection=connection,
                current_game_status=game_status,
                current_game=game,
            )

        connection.commit()
