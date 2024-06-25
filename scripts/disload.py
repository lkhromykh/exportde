import numpy as np
from scipy.spatial.transform import Rotation as R
import exportde

import movements
import bucket_manip


def _r2l(rot_):
    """Rotation to rotvec list."""
    return rot_.as_rotvec().tolist()


def _get_bucket_position(height: float, place: str) -> np.ndarray:
    """Predefined hardcoded positions with varying height."""
    hpi = exportde.hpi
    rot = R.from_rotvec([0, hpi, 0]) * R.from_rotvec([hpi, 0, 0])
    match place:
        case "center":
            position = list(exportde.BUCKET_POSITION_XY) + [height] + _r2l(rot)
        case "right":
            rot = R.from_rotvec([0, 0, hpi]) * rot
            position = [0.2, -exportde.PLATFORM_HALFWIDTH, height] + _r2l(rot)
        case "left":
            rot = R.from_rotvec([0, 0, -hpi]) * rot
            position = [-0.25, exportde.PLATFORM_HALFWIDTH, height] + _r2l(rot)
        case _:
            raise ValueError(place)
    return np.asarray(position)


@exportde.expo_handler
def disload(ifs: exportde.RobotInterfaces, side: exportde.Side) -> list[float]:
    """Pick an object from the platform and place it on the plane on the left or right side."""
    movements.unfold(ifs)
    bucket_pos = _get_bucket_position(exportde.BUCKET_HEIGHT, "center")
    bucket_manip.pick_bucket(ifs, bucket_pos)
    movements.moveZ(ifs, exportde.PEDESTAL_HEIGHT)
    height = ifs.rtde_receive.getActualTCPPose()[2]
    next_pos = _get_bucket_position(height, side)
    ifs.rtde_control.moveJ_IK(next_pos)
    last_known_bucket_pos = bucket_manip.place_bucket(ifs)

    if side == "right":
        rot = R.from_rotvec([0, exportde.hpi, 0])
    else:
        rot = R.from_rotvec([0, -exportde.hpi, 0])
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    rot = rot * R.from_rotvec(tcp_pos[3:])
    tcp_pos = tcp_pos[:3] + _r2l(rot)
    ifs.rtde_control.moveL(tcp_pos)
    movements.unfold(ifs)
    return last_known_bucket_pos


@exportde.expo_handler
def load(ifs: exportde.RobotInterfaces,
         side: exportde.Side,
         last_known_bucket_pos: list[float] | None = None
         ) -> None:
    movements.unfold(ifs)
    if last_known_bucket_pos is not None:
        bucket_pos = last_known_bucket_pos
    else:
        # todo: height should be changed to smthing like BUCKET_HEIGHT - PLATFORM_HEIGHT
        bucket_pos = _get_bucket_position(0.147, side)
    move = bucket_pos.copy()
    move[2] = ifs.rtde_receive.getActualTCPPose()[2]
    pos, rotvec = np.split(np.asarray(move), [3])
    diff = R.from_rotvec(rotvec).apply([0, 0, -0.15])
    ifs.rtde_control.moveJ_IK(np.r_[pos + diff, rotvec])
    bucket_manip.pick_bucket(ifs, bucket_pos)
    ifs.rtde_control.moveL(move)
    center = _get_bucket_position(exportde.BUCKET_HEIGHT + exportde.PEDESTAL_HEIGHT, "center")
    ifs.rtde_control.moveJ_IK(center)
    bucket_manip.place_bucket(ifs)
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    rot = R.from_rotvec([exportde.hpi, 0, 0]) * R.from_rotvec(tcp_pos[3:])
    tcp_pos = tcp_pos[:3] + _r2l(rot)
    ifs.rtde_control.moveL(tcp_pos)
    movements.unfold(ifs)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("python disload.py program side")
        print("-program = disload, load")
        print("-side = left, right")
        exit(1)
    program, side = sys.argv[1:3]
    if program not in ["disload", "load"]:
        print("Unknown program: ", program)
        exit(1)
    if side not in ["left", "right"]:
        print("Wrong argument: ", side)
        exit(1)
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        eval(program)(ifs, side)
