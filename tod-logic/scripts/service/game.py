from datetime import datetime

import MySQLdb

from db import sql_literal
from model import GameModel, GameRecord


_TABLE = "game"


def insert(game: GameModel, connection: MySQLdb.Connection) -> GameRecord:
    with connection.cursor() as cursor:
        query = f"""
        INSERT {_TABLE} (
            `start_time`,
            `end_time`,
            `game_end_reason`
        ) VALUES (
            {sql_literal(game.start_time)},
            {sql_literal(game.end_time)},
            {sql_literal(game.game_end_reason)}
        )
        """

        cursor.execute(query)

        cursor.execute("SELECT LAST_INSERT_ID()")
        id = cursor.fetchone()[0]

    return GameRecord.of(game, id)


def insert_start_game(
    *, start_time: datetime = None, connection: MySQLdb.Connection
) -> GameRecord:
    if start_time is None:
        start_time = datetime.now()

    game = GameModel(start_time=start_time)
    return insert(game, connection=connection)
