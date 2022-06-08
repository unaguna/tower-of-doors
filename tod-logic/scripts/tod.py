#!/usr/bin/env python3

import argparse

from argtype import positive_int
import logic.door
import logic.game
import logic.maintenance


class DoorControlArgs:
    """The arguments of subcommands for door controls."""

    _args: argparse.Namespace

    def __init__(self, args: argparse.Namespace) -> None:
        """The arguments of subcommands for door controls.

        Args:
            args (argparse.Namespace): The arguments got from `argparse` module.
        """
        self._args = args

    @property
    def door_id(self) -> str:
        """ID of door to be controlled."""
        return self._args.door_id

    @property
    def control_all_doors_flg(self) -> bool:
        """If true, all doors are subject to control."""
        return self.door_id.lower() == "all"


class StartGameArgs:
    """The arguments of subcommand to start a game."""

    _args: argparse.Namespace

    def __init__(self, args: argparse.Namespace) -> None:
        """The arguments of subcommand to start a game.

        Args:
            args (argparse.Namespace): The arguments got from `argparse` module.
        """
        self._args = args

    @property
    def player_num(self) -> int:
        """Number of groups of players participating in the game."""
        return self._args.player_num


def command_open_door(_args: argparse.Namespace):
    """Implementation of subcommand to open doors.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    args = DoorControlArgs(_args)

    # TODO: validation

    if args.control_all_doors_flg:
        logic.door.open_all_door()
    else:
        logic.door.open_door(args.door_id)


def command_close_door(_args: argparse.Namespace):
    """Implementation of subcommand to close doors.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    args = DoorControlArgs(_args)

    # TODO: validation

    if args.control_all_doors_flg:
        logic.door.close_all_door()
    else:
        logic.door.close_door(args.door_id)


def command_start_game(_args: argparse.Namespace):
    """Implementation of subcommand to start a game.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    args = StartGameArgs(_args)
    logic.game.start_game(player_num=args.player_num)


def command_end_game(_: argparse.Namespace):
    """Implementation of subcommand to terminate the game.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    logic.game.end_game()


def command_check_maintenance(_: argparse.Namespace):
    """Implementation of subcommand to check whether maintenance is in progress.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    print("command_check_maintenance: Not Implemented")


def command_start_maintenance(_: argparse.Namespace):
    """Implementation of subcommand to start maintenance.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    print("command_start_maintenance: Not Implemented")


def command_end_maintenance(_: argparse.Namespace):
    """Implementation of subcommand to end maintenance.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
    logic.maintenance.end_maintenance()


def arg_parser() -> argparse.ArgumentParser:
    """Build an argument parser of this script.

    Args:
        args (argparse.Namespace): The arguments got from `argparse` module.
    """
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

    parser_maintenance = subparsers.add_parser(
        "maintenance", help="control maintenance"
    )
    maintenance_subparsers = parser_maintenance.add_subparsers()
    parser_maintenance.set_defaults(handler=lambda _: parser_maintenance.print_help())

    parser_add = maintenance_subparsers.add_parser(
        "status", help="show whether the system is in maintenance"
    )
    parser_add.set_defaults(handler=command_check_maintenance)

    parser_add = maintenance_subparsers.add_parser("start", help="start maintenance")
    parser_add.set_defaults(handler=command_start_maintenance)

    parser_add = maintenance_subparsers.add_parser("end", help="end maintenance")
    parser_add.set_defaults(handler=command_end_maintenance)

    return parser


if __name__ == "__main__":
    parser = arg_parser()

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()
