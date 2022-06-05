from datetime import datetime, timedelta
import math
from typing import Tuple

import MySQLdb

from model import YawingReason, YawingScheduleRecord, YawingStatus
import service
import service.azimuthlog
import service.gamestatus
import service.yawingschedule


def _calc_next_azimuth(
    yawing_schedule: YawingScheduleRecord,
    current_azimuth: float,
    interval: timedelta,
    now: datetime = None,
) -> Tuple[float, bool]:
    """Calculate the azimuth angle at the next time based on the yawing schedule.

    Args:
        yawing_schedule (YawingScheduleRecord):
            Schedule to be used in calculations.
            Calculate as if the yawing is as per this schedule.
        current_azimuth (float):
            Azimuth angle at the current time.
            If the argument `now` is specified, the azimuth angle at that time.
        interval (timedelta):
            Recalculation interval.
        now (datetime, optional):
            Calculate the azimuth angle at this time. Defaults to current time.

    Returns:
        Tuple[float, bool]:
            azimuth and whether the yawing continues.
            If the second value is false, the yawing of the specified schedule is complete.
    """
    if now is None:
        now = datetime.now()

    remaining_time = yawing_schedule.schedule_end_time - now
    # Remaining yawing angle
    # The direction of yawing is determined so that the absolute value of the yawing angle is smaller
    remaining_azimuth = min(
        yawing_schedule.aim_azimuth - current_azimuth,
        yawing_schedule.aim_azimuth + 360 - current_azimuth,
        key=abs,
    )

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


def schedule_yaw(
    yawing_angle: float,
    schedule_start_time: datetime,
    schedule_end_time: datetime,
    *,
    connection: MySQLdb.Connection = None
) -> YawingScheduleRecord:
    """Schedule yawing

    Args:
        yawing_angle (float): Angle of yawing
        schedule_start_time (datetime):
            Time to start yawing.
            The yawing actually starts after this time.
        schedule_end_time (datetime):
            Time to complete yawing.
            The rotation is actually completed by this time.
        connection (MySQLdb.Connection, optional):
            Connection to DB.
            If not specified, a new connection is created and committed
            when the job of this function is successfully completed.

    Returns:
        YawingScheduleRecord: Record added to DB by this process
    """
    if connection is None:
        with service.connect() as new_connection:
            scheduled_yawing = schedule_yaw(
                yawing_angle=yawing_angle,
                schedule_start_time=schedule_start_time,
                schedule_end_time=schedule_end_time,
                connection=new_connection,
            )
            new_connection.commit()
        return scheduled_yawing

    current_azimuth = service.azimuthlog.get_current_azimuth(connection=connection)
    next_azimuth = (current_azimuth + yawing_angle) % 360
    scheduled_yawing = service.yawingschedule.insert_schedule(
        aim_azimuth=next_azimuth,
        yawing_reason=YawingReason.GAME_PHASE,
        schedule_start_time=schedule_start_time,
        schedule_end_time=schedule_end_time,
        connection=connection,
    )

    return scheduled_yawing


def azimuth_control(now: datetime, azimuth_update_interval: timedelta):
    """Check yawing schedule and emulate yawing

    All updates to each record associated with yawing are also performed.

    Args:
        now (datetime): current time.
        azimuth_update_interval (timedelta): Azimuth recalculation interval.
    """
    with service.connect() as connection:
        current_yawing = service.yawingschedule.get_now_yawing(connection=connection)
        starting_schedule_id_list = service.yawingschedule.find_id(
            connection=connection,
            yawing_status=YawingStatus.SCHEDULED,
            schedule_start_time_max=now,
        )

        if current_yawing is not None:
            # TODO: semi-error when len(starting_schedule_id_list) > 0

            current_azimuth = service.azimuthlog.get_current_azimuth(
                connection=connection
            )

            # yaw (insert into azimuth_log)
            next_azimuth, is_last_step = _calc_next_azimuth(
                current_yawing,
                current_azimuth,
                interval=azimuth_update_interval,
                now=now,
            )
            service.azimuthlog.insert_azimuth(
                next_azimuth,
                yawing=not is_last_step,
                timestamp=now,
                connection=connection,
            )
            print("yawing: current_azimuth =", next_azimuth)

            # End yawing
            if is_last_step:
                service.yawingschedule.update_end_yawing(
                    current_yawing,
                    connection=connection,
                    actual_end_time=now,
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
