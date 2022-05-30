#!/usr/bin/env python3


import asyncio
from datetime import datetime, timedelta
import math
from typing import Tuple

import MySQLdb

from model import YawingScheduleRecord, YawingStatus
import service
import service.azimuthlog
import service.doorlog
import service.doorstatus
import service.gamestatus
import service.yawingschedule


INTERVAL_TIME_SEC = 300
TURN_TIME_SEC = 300


def calc_next_azimuth(
    yawing_schedule: YawingScheduleRecord,
    current_azimuth: float,
    interval: timedelta,
    now: datetime = None,
) -> Tuple[float, bool]:
    if now is None:
        now = datetime.now()

    remaining_time = yawing_schedule.schedule_end_time - now
    remaining_azimuth = yawing_schedule.aim_azimuth - current_azimuth

    # Number of azimuth change decisions to be made until the scheduled end time.
    remaining_step = max(1, math.floor(remaining_time / interval))

    # Determine the angular velocity so that the yawing is completed by the scheduled end time.
    if remaining_step <= 1:
        next_azimuth = yawing_schedule.aim_azimuth
        is_last_step = True
    else:
        next_azimuth = (remaining_azimuth / remaining_step) + current_azimuth
        is_last_step = False

    return next_azimuth, is_last_step


async def col_initial_connection():
    connection_interval = timedelta(seconds=5)

    while True:
        try:
            with service.connect() as connection:
                game_status = service.gamestatus.get_latest(connection=connection)
            print("Connected to the database successfully.")
            print("Current status:", game_status)

            break
        except MySQLdb.OperationalError as e:
            print("DB Connection failed:", e)
        await asyncio.sleep(connection_interval.total_seconds())


async def col_game_control(
    *, interval_time: timedelta = None, turn_time: timedelta = None
):
    if interval_time is None:
        interval_time = timedelta(seconds=INTERVAL_TIME_SEC)
    if turn_time is None:
        turn_time = timedelta(seconds=TURN_TIME_SEC)

    loop_interval = max(timedelta(seconds=1), min(interval_time, turn_time) / 60)

    loop_period_time = datetime.now()
    while True:
        with service.connect() as connection:
            game_status = service.gamestatus.get_latest(connection=connection)
            game_status_oldness = loop_period_time - game_status.timestamp

            if (
                game_status.on_interval_turn and game_status_oldness >= interval_time
            ) or (game_status.on_someones_turn and game_status_oldness >= turn_time):
                next_game_status = service.gamestatus.insert_next_turn_of(
                    game_status, connection=connection
                )

                # Close doors
                closed_doors = service.doorstatus.get_opened_door_id_list(
                    connection=connection
                )
                for door_id in closed_doors:
                    service.doorlog.insert_close(door_id, connection=connection)

                # log
                print("increased turn to", next_game_status)
                if len(closed_doors) > 0:
                    print("closed doors:", closed_doors)

            connection.commit()

        # calc waiting time for the next loop
        next_loop_period_time = loop_period_time + loop_interval
        remaining_time = next_loop_period_time - datetime.now()

        if remaining_time > timedelta(0):
            await asyncio.sleep(remaining_time.total_seconds())
        loop_period_time = next_loop_period_time


async def col_azimuth_control():
    loop_interval = timedelta(seconds=5)

    loop_period_time = datetime.now()
    while True:
        with service.connect() as connection:
            current_yawing = service.yawingschedule.get_now_yawing(
                connection=connection
            )
            starting_schedule_id_list = service.yawingschedule.find_id(
                connection=connection,
                yawing_status=YawingStatus.SCHEDULED,
                schedule_start_time_max=loop_period_time,
            )

            if current_yawing is not None:
                # TODO: semi-error when len(starting_schedule_id_list) > 0

                current_azimuth = service.azimuthlog.get_current_azimuth(
                    connection=connection
                )

                # yaw (insert into azimuth_log)
                next_azimuth, is_last_step = calc_next_azimuth(
                    current_yawing,
                    current_azimuth,
                    interval=loop_interval,
                    now=loop_period_time,
                )
                service.azimuthlog.insert_azimuth(
                    next_azimuth,
                    yawing=not is_last_step,
                    timestamp=loop_period_time,
                    connection=connection,
                )
                print("yawing: current_azimuth =", next_azimuth)
                if is_last_step:
                    service.yawingschedule.update_end_yawing(
                        current_yawing,
                        connection=connection,
                        actual_end_time=loop_period_time,
                    )
                    print("complete yawing: id =", current_yawing.id)
            else:
                # TODO: semi-error when len(starting_schedule_id_list) >= 2

                # Start yawing
                if len(starting_schedule_id_list) > 0:
                    yawing_schedule_id = starting_schedule_id_list[0]
                    service.yawingschedule.update_start_yawing(
                        yawing_schedule_id, connection=connection
                    )
                    # TODO: output not only id but also aim_azimuth etc.
                    print("start yawing: id =", yawing_schedule_id)

            connection.commit()

        # calc waiting time for the next loop
        next_loop_period_time = loop_period_time + loop_interval
        remaining_time = next_loop_period_time - datetime.now()

        if remaining_time > timedelta(0):
            await asyncio.sleep(remaining_time.total_seconds())
        loop_period_time = next_loop_period_time


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    loop.run_until_complete(col_initial_connection())

    loop.create_task(col_game_control())
    loop.create_task(col_azimuth_control())
    loop.run_forever()
