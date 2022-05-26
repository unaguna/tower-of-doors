#!/usr/bin/env python3

import argparse

import service
import service.doorlog


def command_open_door(args: argparse.Namespace):
    connection = service.connect()

    # TODO: validation
    service.doorlog.insert_open(args.door_id, connection=connection)

    connection.commit()
    connection.close()


def command_close_door(args: argparse.Namespace):
    connection = service.connect()

    # TODO: validation
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
