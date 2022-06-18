from datetime import datetime

import MySQLdb

from db import sql_literal


_TABLE = "game"


def insert_start_game(*, now: datetime = None, connection: MySQLdb.Connection):
    if now is None:
        now = datetime.now()

    with connection.cursor() as cursor:
        query = f"""
        INSERT {_TABLE} (
            `start_time`
        ) VALUES (
            {sql_literal(now)}
        )
        """

        cursor.execute(query)
