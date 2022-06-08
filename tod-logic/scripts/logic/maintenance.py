import service
import service.gamestatus


def end_maintenance():
    """End the maintenance

    If not on maintenance now, it raises an exception.
    """
    with service.connect() as connection:
        service.gamestatus.insert_end_maintenance(connection=connection)

        connection.commit()
