from datetime import datetime

from db import sql_literal


_TABLE = "azimuth_log"


def get_current_azimuth(*, connection) -> float:
    cursor = connection.cursor()

    query = f"""
    SELECT `azimuth` from {_TABLE}
    ORDER BY `timestamp` DESC
    LIMIT 1
    """

    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()

    return row[0]


def insert_azimuth(
    azimuth: float, *, connection, yawing: bool = True, timestamp: datetime = None
):
    if timestamp is None:
        timestamp = datetime.now()

    azimuth %= 360

    cursor = connection.cursor()

    query = f"""
    INSERT INTO {_TABLE} (
        `azimuth`,
        `timestamp`,
        `yawing`
    ) VALUES (
        {sql_literal(azimuth)},
        {sql_literal(timestamp)},
        {sql_literal(yawing)}
    )
    """

    cursor.execute(query)
    cursor.close()
