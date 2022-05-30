from datetime import datetime

import MySQLdb

from db import sql_literal
from model import GAME_STATUS_FIELDS, GameStatusRecord


_TABLE = "game_status"


def get_latest(*, connection) -> GameStatusRecord:
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    query = f"""
    SELECT 
        {",".join(f"`{f}`" for f in GAME_STATUS_FIELDS)}
    FROM {_TABLE}
    ORDER BY `timestamp`
    DESC LIMIT 1
    """

    cursor.execute(query)
    row = cursor.fetchone()

    return GameStatusRecord(
        status=row["status"],
        player_num=row["player_num"],
        turn_player=row["turn_player"],
        timestamp=row["timestamp"],
    )


def insert(game_status: GameStatusRecord, *, connection):
    cursor = connection.cursor()

    query = f"""
    INSERT {_TABLE} (
        `status`,
        `player_num`,
        `turn_player`,
        `timestamp`
    ) VALUES (
        {sql_literal(game_status.status)},
        {sql_literal(game_status.player_num)},
        {sql_literal(game_status.turn_player)},
        {sql_literal(game_status.timestamp.isoformat())}
    )
    """

    cursor.execute(query)


def insert_start_game(
    player_num: int, current_game_status: GameStatusRecord = None, *, connection
) -> GameStatusRecord:
    if current_game_status is None:
        current_game_status = get_latest(connection=connection)

    if current_game_status.on_game:
        raise Exception(
            "cannot insert into `game_status`: cannot start game: already started"
        )
    elif current_game_status.on_maintenance:
        raise Exception(
            "cannot insert into `game_status`: cannot start game: now on maintenance"
        )
    else:
        start_game_status = GameStatusRecord(
            status="ON_GAME",
            player_num=player_num,
            turn_player=0,
            timestamp=datetime.now(),
        )
        insert(start_game_status, connection=connection)

        return start_game_status


def insert_end_game(
    current_game_status: GameStatusRecord = None, *, connection
) -> GameStatusRecord:
    if current_game_status is None:
        current_game_status = get_latest(connection=connection)

    if not current_game_status.on_game:
        raise Exception(
            "cannot insert into `game_status`: cannot end game: not on game"
        )
    else:
        end_game_status = GameStatusRecord(
            status="STANDBY",
            player_num=None,
            turn_player=None,
            timestamp=datetime.now(),
        )
        insert(end_game_status, connection=connection)

        return end_game_status


def insert_next_turn_of(
    current_game_status: GameStatusRecord, *, connection
) -> GameStatusRecord:
    if not current_game_status.on_game:
        raise Exception(
            "cannot insert into `game_status`: cannot increase turn when not on game"
        )

    next_turn = (current_game_status.turn_player + 1) % (
        current_game_status.player_num + 1
    )

    next_game_status = GameStatusRecord(
        timestamp=datetime.now(),
        turn_player=next_turn,
        status=current_game_status.status,
        player_num=current_game_status.player_num,
    )

    insert(next_game_status, connection=connection)

    return next_game_status