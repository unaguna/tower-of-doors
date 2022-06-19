from datetime import datetime, timedelta

import MySQLdb

from db import sql_literal
from model import GameEndReason, GameModel, GameRecord


_TABLE = "game"


def get_by_id(id: int, connection: MySQLdb.Connection) -> GameRecord:
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    query = f"""
    SELECT
        {",".join(f"`{f}`" for f in GameRecord.fields())}
    FROM {_TABLE}
    WHERE `id` = {id}
    LIMIT 1
    """

    cursor.execute(query)
    row = cursor.fetchone()

    return GameRecord(
        id=row["id"],
        player_num=row["player_num"],
        interval_period=timedelta(milliseconds=row["interval_period"]),
        player_period=timedelta(milliseconds=row["player_period"]),
        start_time=row["start_time"],
        end_time=row["end_time"],
        game_end_reason=GameEndReason.or_none(row["game_end_reason"]),
    )


def insert(game: GameModel, connection: MySQLdb.Connection) -> GameRecord:
    with connection.cursor() as cursor:
        query = f"""
        INSERT {_TABLE} (
            `player_num`,
            `interval_period`,
            `player_period`,
            `start_time`,
            `end_time`,
            `game_end_reason`
        ) VALUES (
            {sql_literal(game.player_num)},
            {sql_literal(game.interval_period)},
            {sql_literal(game.player_period)},
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
    player_num: int,
    *,
    interval_period: timedelta,
    player_period: timedelta,
    start_time: datetime = None,
    connection: MySQLdb.Connection,
) -> GameRecord:
    if start_time is None:
        start_time = datetime.now()

    game = GameModel(
        player_num=player_num,
        interval_period=interval_period,
        player_period=player_period,
        start_time=start_time,
    )
    return insert(game, connection=connection)


def update_end_game(
    id: int,
    game_end_reason: GameEndReason,
    end_time: datetime = None,
    *,
    connection: MySQLdb.Connection,
):
    if end_time is None:
        end_time = datetime.now()

    with connection.cursor() as cursor:
        query = f"""
        UPDATE {_TABLE} SET
            `end_time` = {sql_literal(end_time)},
            `game_end_reason` = {sql_literal(game_end_reason)}
        WHERE
            `id` = {sql_literal(id)}
        """

        cursor.execute(query)
