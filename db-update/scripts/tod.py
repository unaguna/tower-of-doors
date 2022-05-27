#!/usr/bin/env python3

import argparse

import service
import service.door
import service.doorlog


class DoorControlArgs:
    _args: argparse.Namespace

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

    @property
    def door_id(self) -> str:
        return self._args.door_id

    @property
    def control_all_doors_flg(self) -> bool:
        return self.door_id.lower() == "all"


def command_open_door(_args: argparse.Namespace):
    args = DoorControlArgs(_args)

    connection = service.connect()

    # TODO: validation

    if args.control_all_doors_flg:
        door_id_list = service.door.id_list(connection=connection)
        for door_id in door_id_list:
            service.doorlog.insert_open(door_id, connection=connection)
    else:
        service.doorlog.insert_open(args.door_id, connection=connection)

    connection.commit()
    connection.close()


def command_close_door(_args: argparse.Namespace):
    args = DoorControlArgs(_args)

    connection = service.connect()

    # TODO: validation

    if args.control_all_doors_flg:
        door_id_list = service.door.id_list(connection=connection)
        for door_id in door_id_list:
            service.doorlog.insert_close(door_id, connection=connection)
    else:
        service.doorlog.insert_close(args.door_id, connection=connection)

    connection.commit()
    connection.close()


def arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control Tower of Doors")
    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser("open", help="open a door manually")
    parser_add.add_argument("door_id", type=str, help="The door id")
    parser_add.set_defaults(handler=command_open_door)

    parser_add = subparsers.add_parser("close", help="close a door manually")
    parser_add.add_argument("door_id", type=str, help="The door id")
    parser_add.set_defaults(handler=command_close_door)

    return parser


if __name__ == "__main__":
    parser = arg_parser()

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()
