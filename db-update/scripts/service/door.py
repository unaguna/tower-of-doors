from typing import Sequence


_TABLE = "door"


def id_list(*, connection) -> Sequence[str]:
    cursor = connection.cursor()

    query = f"""
    SELECT id FROM {_TABLE}
    """

    cursor.execute(query)
    cursor.close()

    return list(map(lambda r: r[0], cursor))
