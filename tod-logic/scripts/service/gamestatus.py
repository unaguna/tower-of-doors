from datetime import datetime

import MySQLdb

from db import sql_literal
from model import GAME_STATUS_FIELDS, GameStatus, GameStatusRecord


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
        status=GameStatus(row["status"]),
        game_id=row["game_id"],
        turn_player=row["turn_player"],
        timestamp=row["timestamp"],
    )


def insert(game_status: GameStatusRecord, *, connection):
    cursor = connection.cursor()

    query = f"""
    INSERT {_TABLE} (
        `status`,
        `game_id`,
        `turn_player`,
        `timestamp`
    ) VALUES (
        {sql_literal(game_status.status)},
        {sql_literal(game_status.game_id)},
        {sql_literal(game_status.turn_player)},
        {sql_literal(game_status.timestamp.isoformat())}
    )
    """

    cursor.execute(query)


def insert_start_maintenance(
    current_game_status: GameStatusRecord = None,
    now: datetime = None,
    *,
    connection: MySQLdb.Connection,
) -> GameStatusRecord:
    if now is None:
        now = datetime.now()
    if current_game_status is None:
        current_game_status = get_latest(connection=connection)

    if current_game_status.on_maintenance:
        raise Exception(
            "cannot insert into `game_status`: cannot start maintenance: already in maintenance"
        )
    else:
        start_maintenance_status = GameStatusRecord(
            status=GameStatus.MAINTENANCE,
            game_id=None,
            turn_player=None,
            timestamp=now,
        )
        insert(start_maintenance_status, connection=connection)

        return start_maintenance_status


def insert_end_maintenance(
    current_game_status: GameStatusRecord = None, *, connection: MySQLdb.Connection
) -> GameStatusRecord:
    if current_game_status is None:
        current_game_status = get_latest(connection=connection)

    if not current_game_status.on_maintenance:
        raise Exception(
            "cannot insert into `game_status`: cannot end maintenance: not in maintenance now"
        )
    else:
        end_maintenance_status = GameStatusRecord(
            status=GameStatus.STANDBY,
            game_id=None,
            turn_player=None,
            timestamp=datetime.now(),
        )
        insert(end_maintenance_status, connection=connection)

        return end_maintenance_status


def insert_start_game(
    game_id: int,
    current_game_status: GameStatusRecord = None,
    now: datetime = None,
    *,
    connection: MySQLdb.Connection,
) -> GameStatusRecord:
    if now is None:
        now = datetime.now()
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
            status=GameStatus.ON_GAME,
            game_id=game_id,
            turn_player=0,
            timestamp=now,
        )
        insert(start_game_status, connection=connection)

        return start_game_status


def insert_end_game(
    current_game_status: GameStatusRecord = None, now: datetime = None, *, connection
) -> GameStatusRecord:
    if now is None:
        now = datetime.now()
    if current_game_status is None:
        current_game_status = get_latest(connection=connection)

    if not current_game_status.on_game:
        raise Exception(
            "cannot insert into `game_status`: cannot end game: not on game"
        )
    else:
        end_game_status = GameStatusRecord(
            status=GameStatus.STANDBY,
            game_id=None,
            turn_player=None,
            timestamp=now,
        )
        insert(end_game_status, connection=connection)

        return end_game_status


def insert_next_turn_of(
    current_game_status: GameStatusRecord, player_num: int, *, connection
) -> GameStatusRecord:
    if not current_game_status.on_game:
        raise Exception(
            "cannot insert into `game_status`: cannot increase turn when not on game"
        )

    next_turn = (current_game_status.turn_player + 1) % (player_num + 1)

    next_game_status = GameStatusRecord(
        timestamp=datetime.now(),
        game_id=current_game_status.game_id,
        turn_player=next_turn,
        status=current_game_status.status,
    )

    insert(next_game_status, connection=connection)

    return next_game_status
