import service
import service.door
import service.doorlog


def open_door(door_id: str):
    with service.connect() as connection:
        service.doorlog.insert_open(door_id, connection=connection)

        connection.commit()


def open_all_door():
    with service.connect() as connection:
        door_id_list = service.door.id_list(connection=connection)
        for door_id in door_id_list:
            service.doorlog.insert_open(door_id, connection=connection)

        connection.commit()


def close_door(door_id: str):
    with service.connect() as connection:
        service.doorlog.insert_close(door_id, connection=connection)

        connection.commit()


def close_all_door():
    with service.connect() as connection:
        door_id_list = service.door.id_list(connection=connection)
        for door_id in door_id_list:
            service.doorlog.insert_close(door_id, connection=connection)

        connection.commit()
