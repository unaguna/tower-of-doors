def positive_int(value: str) -> int:
    try:
        value_int = int(value)
    except ValueError:
        raise ValueError(
            f"invalid literal for positive_int() with base 10: {repr(value)}"
        )

    if value_int > 0:
        return value_int
    else:
        raise ValueError(
            f"invalid literal for positive_int() with base 10: {repr(value)}"
        )
