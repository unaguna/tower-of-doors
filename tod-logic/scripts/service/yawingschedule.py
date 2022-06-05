from datetime import datetime
from typing import Sequence

import MySQLdb

from db import sql_literal
from model import (
    YawingReason,
    YAWING_SCHEDULE_FIELDS,
    YawingScheduleRecord,
    YawingStatus,
)


_TABLE = "yawing_schedule"


def get_now_yawing(*, connection) -> YawingScheduleRecord | None:
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    query = f"""
    SELECT 
        {",".join(f"`{f}`" for f in YAWING_SCHEDULE_FIELDS)}
    FROM {_TABLE}
    WHERE `yawing_status` = {sql_literal(YawingStatus.ON_YAWING)}
    LIMIT 1
    """

    cursor.execute(query)
    row = cursor.fetchone()

    if row is not None:
        return YawingScheduleRecord(
            id=row["id"],
            aim_azimuth=row["aim_azimuth"],
            yawing_reason=YawingReason(row["yawing_reason"]),
            schedule_start_time=row["schedule_start_time"],
            schedule_end_time=row["schedule_end_time"],
            yawing_status=YawingStatus(row["yawing_status"]),
            actual_start_time=row["actual_start_time"],
            actual_end_time=row["actual_end_time"],
        )
    else:
        return None


def find_id(
    *,
    connection,
    limit: int | None = None,
    yawing_status: YawingStatus | None = None,
    schedule_start_time_max: datetime | None = None,
) -> Sequence[int]:
    # Build where statement
    where_statement_expressions = list()
    if yawing_status is not None:
        where_statement_expressions.append(
            f"`yawing_status`={sql_literal(yawing_status)}"
        )
    if schedule_start_time_max is not None:
        where_statement_expressions.append(
            f"`schedule_start_time`<={sql_literal(schedule_start_time_max)}"
        )
    if len(where_statement_expressions) > 0:
        where_statement = "WHERE " + " and ".join(where_statement_expressions)
    else:
        where_statement = ""

    # Build limit statement
    if limit is not None:
        limit_statement = f"LIMIT {limit}"
    else:
        limit_statement = ""

    cursor = connection.cursor()

    query = f"""
    SELECT id FROM {_TABLE}
    {where_statement}
    {limit_statement}
    ORDER BY `schedule_start_time`
    """

    cursor.execute(query)
    cursor.close()

    return list(map(lambda r: r[0], cursor))


def insert_schedule(
    aim_azimuth: float,
    yawing_reason: YawingReason,
    schedule_start_time: datetime,
    schedule_end_time: datetime,
    *,
    connection,
) -> YawingScheduleRecord:
    yawing_schedule: YawingScheduleRecord = YawingScheduleRecord(
        aim_azimuth=aim_azimuth,
        yawing_reason=yawing_reason,
        schedule_start_time=schedule_start_time,
        schedule_end_time=schedule_end_time,
        yawing_status=YawingStatus.SCHEDULED,
        # TODO: dataclass を使用する際に、不要な引数があれば削除
        id=None,
        actual_start_time=None,
        actual_end_time=None,
    )

    cursor = connection.cursor()

    query = f"""
    insert into {_TABLE} (
        aim_azimuth,
        yawing_reason,
        schedule_start_time,
        schedule_end_time,
        yawing_status
    ) VALUES (
        {sql_literal(yawing_schedule.aim_azimuth)},
        {sql_literal(yawing_schedule.yawing_reason)},
        {sql_literal(yawing_schedule.schedule_start_time)},
        {sql_literal(yawing_schedule.schedule_end_time)},
        {sql_literal(yawing_schedule.yawing_status)}
    )
    """
    cursor.execute(query)

    cursor.execute("SELECT LAST_INSERT_ID()")
    id = cursor.fetchone()[0]
    cursor.close()

    # TODO: dataclass を使用する際に代入が可能になっていればコメントアウト
    # yawing_schedule.id = id
    return yawing_schedule


def update_start_yawing(
    id: int,
    *,
    connection,
    actual_start_time: datetime = None,
):
    if actual_start_time is None:
        actual_start_time = datetime.now()

    cursor = connection.cursor()

    query = f"""
    UPDATE {_TABLE}
    SET
        `yawing_status` = {sql_literal(YawingStatus.ON_YAWING)},
        `actual_start_time` = {sql_literal(actual_start_time)}
    WHERE `id` = {sql_literal(id)} and `yawing_status` = {sql_literal(YawingStatus.SCHEDULED)}
    """

    cursor.execute(query)
    cursor.close()


def update_end_yawing(
    id: int | YawingScheduleRecord,
    *,
    connection,
    actual_end_time: datetime = None,
):
    if isinstance(id, YawingScheduleRecord):
        id = id.id
    if actual_end_time is None:
        actual_end_time = datetime.now()

    cursor = connection.cursor()

    query = f"""
    UPDATE {_TABLE}
    SET
        `yawing_status` = {sql_literal(YawingStatus.COMPLETED)},
        `actual_end_time` = {sql_literal(actual_end_time)}
    WHERE `id` = {sql_literal(id)} and `yawing_status` = {sql_literal(YawingStatus.ON_YAWING)}
    """

    cursor.execute(query)
    cursor.close()
