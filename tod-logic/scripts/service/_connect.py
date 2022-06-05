import MySQLdb


def connect() -> MySQLdb.Connection:
    """Connect our database"""
    return MySQLdb.connect(
        read_default_file="/root/.my.cnf",
    )
