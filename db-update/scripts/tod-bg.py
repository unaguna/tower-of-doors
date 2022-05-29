#!/usr/bin/env python3


import asyncio
from datetime import datetime, timedelta

import service
import service.doorlog
import service.doorstatus
import service.gamestatus


INTERVAL_TIME_SEC = 300
TURN_TIME_SEC = 300


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


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(col_game_control())

    loop.run_forever()
