"""Specifically for Sampo without central pos"""
from typing import Optional

from scipy.spatial.transform import Rotation as R
import exportde

from exportde.primitives import movements
from exportde.primitives import bucket_manip
from disload import _get_bucket_position, _r2l


def get_bucket_position(height: float, place: exportde.Side) -> exportde.Position:
    assert place != "center"
    return _get_bucket_position(height, place)


@exportde.expo_handler
def lift_down(ifs: exportde.RobotInterfaces, side: exportde.Side) -> exportde.Position:
    """Pick an object from the platform and place it on the plane on the left or right side."""
    pose = get_bucket_position(0, side)
    ifs.rtde_control.moveJ_IK(pose)
    height = exportde.BUCKET_HEIGHT - exportde.PLATFORM_HEIGHT
    last_known_bucket_pose = bucket_manip.place_bucket(ifs, height)
    if side == "right":
        rot = R.from_rotvec([0, exportde.hpi, 0])
    else:
        rot = R.from_rotvec([0, -exportde.hpi, 0])
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    rot = rot * R.from_rotvec(tcp_pos[3:])
    tcp_pos = tcp_pos[:3] + _r2l(rot)
    ifs.rtde_control.moveL(tcp_pos)
    movements.unfold(ifs)
    return last_known_bucket_pose


@exportde.expo_handler
def lift_up(ifs: exportde.RobotInterfaces,
       side: exportde.Side,
       last_known_bucket_pos: Optional[exportde.Position] = None
       ) -> None:
    movements.unfold(ifs)
    if last_known_bucket_pos is None:
        bucket_pos = _get_bucket_position(exportde.BUCKET_HEIGHT - exportde.PLATFORM_HEIGHT, side)
    else:
        bucket_pos = last_known_bucket_pos
    top_pose = bucket_pos.copy()
    top_pose[2] = ifs.rtde_receive.getActualTCPPose()[2]
    bucket_manip.pick_bucket(ifs, bucket_pos)
    ifs.rtde_control.moveL(top_pose)


if __name__ == "__main__":
    import time
    import argparse

    parser = argparse.ArgumentParser(prog="bucket_lifts.py")
    parser.add_argument("program", choices=["up", "down", "cycle"])
    parser.add_argument("side", choices=["left", "right"])
    args = parser.parse_args()

    program = args.program
    side = args.side
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        if program == "up":
            lift_up(ifs, side)
        elif program == "down":
            lift_down(ifs, side)
        elif program == "cycle":
            sleep_time = 3.0
            while True:
                bucket_pos = lift_down(ifs, side)
                time.sleep(sleep_time)
                lift_up(ifs, side, bucket_pos)
                time.sleep(sleep_time)
