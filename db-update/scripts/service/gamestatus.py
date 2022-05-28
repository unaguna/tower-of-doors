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
