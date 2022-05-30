from datetime import datetime
from enum import Enum
from numbers import Real


def sql_literal(value: any) -> str:
    if value is None:
        return "NULL"
    elif type(value) == str:
        return f"'{value}'"
    elif type(value) == bool:
        return str(value)
    elif isinstance(value, Enum):
        return sql_literal(value.value)
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    elif isinstance(value, Real):
        return str(value)
    else:
        ValueError(f"Unknown literal: {repr(value)}")
