import os

import MySQLdb


def connect(*, host: str = None):
    if host is None:
        host = os.environ.get("MYSQL_HOST", "127.0.0.1")

    return MySQLdb.connect(
        host=host,
        user="root",
        passwd="pass",
        db="tod",
    )
