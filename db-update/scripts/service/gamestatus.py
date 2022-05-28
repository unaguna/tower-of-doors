from datetime import datetime

import MySQLdb

from model import GAME_STATUS_FIELDS, GameStatusRecord


_TABLE = "game_status"


def get_latest(*, connection) -> GameStatusRecord | None:
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
        '{game_status.status}',
        {game_status.player_num},
        {game_status.turn_player},
        '{game_status.timestamp.isoformat()}'
    )
    """

    cursor.execute(query)


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
