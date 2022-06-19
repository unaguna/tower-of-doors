from datetime import datetime

from model import GameEndReason
import service
import service.game
import service.gamestatus


def now_on_maintenance() -> bool:
    """Check whether maintenance is in progress"""
    with service.connect() as connection:
        current_game_status = service.gamestatus.get_latest(connection=connection)

    return current_game_status.on_maintenance


def start_maintenance(force_maintenance: bool):
    """Start the maintenance

    If cannot start maintenance, it raises an exception.

    Args:
        force_maintenance (bool): If true, start maintenance even during the game.
    """
    now = datetime.now()
    with service.connect() as connection:
        current_game_status = service.gamestatus.get_latest(connection=connection)

        if not force_maintenance and current_game_status.on_game:
            raise Exception("cannot start maintenance: now on game")

        service.gamestatus.insert_start_maintenance(
            current_game_status=current_game_status, now=now, connection=connection
        )

        if current_game_status.on_game:
            service.game.update_end_game(
                id=current_game_status.game_id,
                game_end_reason=GameEndReason.MAINTENANCE,
                end_time=now,
                connection=connection,
            )

        connection.commit()


def end_maintenance():
    """End the maintenance

    If not on maintenance now, it raises an exception.
    """
    with service.connect() as connection:
        service.gamestatus.insert_end_maintenance(connection=connection)

        connection.commit()
