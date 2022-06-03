import os

import MySQLdb


def connect() -> MySQLdb.Connection:
    return MySQLdb.connect(
        read_default_file="/root/.my.cnf",
        db="tod",
    )
