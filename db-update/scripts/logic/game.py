from datetime import datetime, timedelta

import MySQLdb

import logic.azimuth
from model import GameStatusRecord, YawingReason
import service
import service.azimuthlog
import service.doorlog
import service.doorstatus
import service.gamestatus
import service.yawingschedule


def start_game(
    player_num: int,
):
    with service.connect() as connection:
        service.gamestatus.insert_start_game(player_num, connection=connection)
        # TODO: start yawing because the game will start with interval-turn
        connection.commit()


def end_game():
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
