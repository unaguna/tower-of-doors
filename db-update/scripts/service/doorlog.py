from datetime import datetime

from model import DoorLogRecord, DoorStatus


_TABLE = "door_log"


def insert(door_log: DoorLogRecord, *, connection):
    cursor = connection.cursor()

    query = f"""
    INSERT {_TABLE} (
        door_id,
        status,
        timestamp,
        reason
    ) VALUES (
        '{door_log.door_id}',
        {door_log.status.value},
        '{door_log.timestamp.isoformat()}',
        '{door_log.reason}'
    )
    """

    cursor.execute(query)


def insert_open(door: str, *, timestamp: datetime | None = None, connection):
    if timestamp is None:
        timestamp = datetime.now()

    door_log = DoorLogRecord(
        door_id=door, status=DoorStatus.OPEN, timestamp=timestamp, reason="REMOTE"
    )

    insert(door_log, connection=connection)


def insert_close(door: str, *, timestamp: datetime | None = None, connection):
    if timestamp is None:
        timestamp = datetime.now()

    door_log = DoorLogRecord(
        door_id=door, status=DoorStatus.CLOSED, timestamp=timestamp, reason="REMOTE"
    )

    insert(door_log, connection=connection)
