#!/usr/bin/env python3

import argparse
from cmath import log

from argtype import positive_int
import logic.game
import service
import service.door
import service.doorlog
import service.gamestatus


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


class StartGameArgs:
    _args: argparse.Namespace

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

    @property
    def player_num(self) -> int:
        return self._args.player_num


def command_open_door(_args: argparse.Namespace):
    args = DoorControlArgs(_args)

    # TODO: validation

    with service.connect() as connection:
        if args.control_all_doors_flg:
            door_id_list = service.door.id_list(connection=connection)
            for door_id in door_id_list:
                service.doorlog.insert_open(door_id, connection=connection)
        else:
            service.doorlog.insert_open(args.door_id, connection=connection)

        connection.commit()


def command_close_door(_args: argparse.Namespace):
    args = DoorControlArgs(_args)

    # TODO: validation

    with service.connect() as connection:
        if args.control_all_doors_flg:
            door_id_list = service.door.id_list(connection=connection)
            for door_id in door_id_list:
                service.doorlog.insert_close(door_id, connection=connection)
        else:
            service.doorlog.insert_close(args.door_id, connection=connection)

        connection.commit()


def command_start_game(_args: argparse.Namespace):
    args = StartGameArgs(_args)
    logic.game.start_game(player_num=args.player_num)


def command_end_game(_: argparse.Namespace):
    logic.game.end_game()


def arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control Tower of Doors")
    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser("start", help="start a game")
    parser_add.add_argument(
        "player_num", type=positive_int, help="The number of players"
    )
    parser_add.set_defaults(handler=command_start_game)

    parser_add = subparsers.add_parser("end", help="end the game")
    parser_add.set_defaults(handler=command_end_game)

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
