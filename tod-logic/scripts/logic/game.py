from datetime import datetime, timedelta

import MySQLdb

import logic.azimuth
from model import GameStatusRecord
import service
import service.azimuthlog
import service.doorlog
import service.doorstatus
import service.game
import service.gamestatus
import service.yawingschedule


def start_game(
    player_num: int,
):
    """Start a game

    Args:
        player_num (int):
            Number of groups of players participating in the game.
    """
    now = datetime.now()
    with service.connect() as connection:
        service.game.insert_start_game(connection=connection, now=now)

        service.gamestatus.insert_start_game(player_num, connection=connection, now=now)
        # TODO: start yawing because the game will start with interval-turn
        connection.commit()


def end_game():
    """Terminate a game"""
    with service.connect() as connection:
        service.gamestatus.insert_end_game(connection=connection)
        connection.commit()


def make_turn_next(
    interval_time: timedelta,
    turn_time: timedelta,
    now: datetime,
    *,
    connection: MySQLdb.Connection = None,
    current_game_status: GameStatusRecord = None,
):
    """Progressing game phases

    Execution of this function will move to the next phase regardless of the time remaining.
    If you want to move to the next phase only when there is no time remaining,
    use `make_turn_next_with_judge()`.

    Args:
        interval_time (timedelta, optional):
            Duration of interval phase
        turn_time (timedelta, optional):
            Duration of each user's phase
        now (datetime):
            current time
        connection (MySQLdb.Connection, optional):
            Connection to DB.
            If not specified, a new connection is created and committed
            when the job of this function is successfully completed.
        current_game_status (GameStatusRecord, optional):
            Current game state.
            If not specified, retrieve from DB.
    """
    if connection is None:
        with service.connect() as new_connection:
            make_turn_next(
                interval_time=interval_time,
                turn_time=turn_time,
                now=now,
                connection=new_connection,
                current_game_status=current_game_status,
            )
            new_connection.commit()
        return

    if current_game_status is None:
        current_game_status = service.gamestatus.get_latest(connection=connection)

    # Move turn next
    next_game_status = service.gamestatus.insert_next_turn_of(
        current_game_status, connection=connection
    )

    # Close doors
    closed_doors = service.doorstatus.get_opened_door_id_list(connection=connection)
    for door_id in closed_doors:
        service.doorlog.insert_close(door_id, connection=connection)

    # schedule yawing
    if next_game_status.on_interval_turn:
        schedule_end_time = now + (interval_time) * 4 / 5
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


def make_turn_next_with_judge(
    interval_time: timedelta,
    turn_time: timedelta,
    now: datetime,
):
    """Progressing game phases if there is no time remaining.

    Args:
        interval_time (timedelta, optional):
            Duration of interval phase
        turn_time (timedelta, optional):
            Duration of each user's phase
        now (datetime):
            current time
    """
    with service.connect() as connection:
        game_status = service.gamestatus.get_latest(connection=connection)
        game_status_oldness = now - game_status.timestamp

        if (game_status.on_interval_turn and game_status_oldness >= interval_time) or (
            game_status.on_someones_turn and game_status_oldness >= turn_time
        ):
            make_turn_next(
                interval_time=interval_time,
                turn_time=turn_time,
                now=now,
                connection=connection,
                current_game_status=game_status,
            )

        connection.commit()
