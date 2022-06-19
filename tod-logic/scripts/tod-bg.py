#!/usr/bin/env python3


import asyncio
from datetime import datetime, timedelta

import MySQLdb

import logic.azimuth
import logic.game
import service
import service.gamestatus


async def col_initial_connection():
    """Attempt to connect to DB until success

    If a connection to the DB is established, output the records that were obtained.
    """
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


async def col_game_control():
    """Control the progress of the game

    Periodically check the state of the game and perform game state transitions
    such as turn progression.
    """
    loop_interval = timedelta(seconds=1)

    loop_period_time = datetime.now()
    while True:
        logic.game.make_turn_next_with_judge(now=loop_period_time)

        # calc waiting time for the next loop
        next_loop_period_time = loop_period_time + loop_interval
        remaining_time = next_loop_period_time - datetime.now()

        if remaining_time > timedelta(0):
            await asyncio.sleep(remaining_time.total_seconds())
        loop_period_time = next_loop_period_time


async def col_azimuth_control():
    """Control the azimuth of the tower

    Periodically check the schedule of yawing and perform yawing (i.e. update azimuth).
    """
    loop_interval = timedelta(seconds=5)

    loop_period_time = datetime.now()
    while True:
        logic.azimuth.azimuth_control(
            now=loop_period_time, azimuth_update_interval=loop_interval
        )

        # calc waiting time for the next loop
        next_loop_period_time = loop_period_time + loop_interval
        remaining_time = next_loop_period_time - datetime.now()

        if remaining_time > timedelta(0):
            await asyncio.sleep(remaining_time.total_seconds())
        loop_period_time = next_loop_period_time


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    # Wait for DB to start up
    # This is because this script may be executed before the DB is launched
    # if the docker containers are launched at the same time.
    loop.run_until_complete(col_initial_connection())

    loop.create_task(col_game_control())
    loop.create_task(col_azimuth_control())
    loop.run_forever()
