from datetime import datetime, timedelta

from model import YawingReason
import service
import service.azimuthlog
import service.doorlog
import service.doorstatus
import service.gamestatus
import service.yawingschedule


def start_game(
    player_num: int,
):
    with service.connect() as connection:
        service.gamestatus.insert_start_game(player_num, connection=connection)
        # TODO: start yawing because the game will start with interval-turn
        connection.commit()


def end_game():
    with service.connect() as connection:
        service.gamestatus.insert_end_game(connection=connection)
        connection.commit()


def make_turn_next_with_judge(
    interval_time: timedelta,
    turn_time: timedelta,
    now: datetime,
):
    with service.connect() as connection:
        game_status = service.gamestatus.get_latest(connection=connection)
        game_status_oldness = now - game_status.timestamp

        if (game_status.on_interval_turn and game_status_oldness >= interval_time) or (
            game_status.on_someones_turn and game_status_oldness >= turn_time
        ):
            # Move turn next
            next_game_status = service.gamestatus.insert_next_turn_of(
                game_status, connection=connection
            )

            # Close doors
            closed_doors = service.doorstatus.get_opened_door_id_list(
                connection=connection
            )
            for door_id in closed_doors:
                service.doorlog.insert_close(door_id, connection=connection)

            # schedule yawing
            if next_game_status.on_interval_turn:
                current_azimuth = service.azimuthlog.get_current_azimuth(
                    connection=connection
                )
                next_azimuth = (current_azimuth + 60) % 360
                schedule_end_time = now + (interval_time) * 4 / 5
                scheduled_yawing = service.yawingschedule.insert_schedule(
                    aim_azimuth=next_azimuth,
                    yawing_reason=YawingReason.GAME_PHASE,
                    schedule_start_time=now,
                    schedule_end_time=schedule_end_time,
                    connection=connection,
                )
            else:
                scheduled_yawing = None

            # log
            print("increased turn to", next_game_status)
            if len(closed_doors) > 0:
                print("closed doors:", closed_doors)
            if scheduled_yawing is not None:
                print("yawing scheduled:", scheduled_yawing)

        connection.commit()
