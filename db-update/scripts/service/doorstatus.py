from typing import Sequence

from db import sql_literal
from model import DoorStatus

_TABLE = "door_status"


def get_opened_door_id_list(*, connection) -> Sequence[str]:
    cursor = connection.cursor()

    query = f"""
    SELECT id FROM {_TABLE}
    WHERE status = {sql_literal(DoorStatus.OPEN)}
    """

    cursor.execute(query)
    cursor.close()

    return list(map(lambda r: r[0], cursor))
