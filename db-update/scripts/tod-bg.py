#!/usr/bin/env python3


import asyncio
from datetime import timedelta


INTERVAL_TIME_SEC = 300
TURN_TIME_SEC = 300


async def col_game_control(
    *, interval_time: timedelta = None, turn_time: timedelta = None
):
    if interval_time is None:
        interval_time = timedelta(seconds=INTERVAL_TIME_SEC)
    if turn_time is None:
        turn_time = timedelta(seconds=TURN_TIME_SEC)

    while True:
        # TODO: implement
        await asyncio.sleep(2)
        print("foo", interval_time)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(col_game_control())

    loop.run_forever()
