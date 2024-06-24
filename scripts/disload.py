import exportde

import movements
import bucket_manip

RIGHT_ROTVEC = [0, exportde.hpi, 0]
LEFT_ROTVEC = [2.221, 0, -2.221]


def _get_bucket_position(height: float, place: str) -> exportde.Position:
    match place:
        case "center":
            return [-0.4255, 0, height, 1.20919958, 1.20919958, -1.20919958]
        case "right":
            return [0.2, -exportde.PLATFORM_HALFWIDTH, height, 0, exportde.hpi, 0]
        case "left":
            return [-0.25, exportde.PLATFORM_HALFWIDTH, height, 2.221, 0, -2.221]
        case _:
            raise ValueError(place)


@exportde.expo_handler
def disload(ifs: exportde.RobotInterfaces, side: exportde.Side) -> None:
    movements.unfold(ifs)
    bucket_pos = _get_bucket_position(exportde.BUCKET_HEIGHT, "center")
    bucket_manip.pick_bucket(ifs, bucket_pos)
    height = ifs.rtde_receive.getActualTCPPose()[2]
    match side:
        case "right":
            next_pos = [0.2, -exportde.PLATFORM_HALFWIDTH, height] + RIGHT_ROTVEC
        case "left":
            next_pos = [-0.25, exportde.PLATFORM_HALFWIDTH, height] + LEFT_ROTVEC
        case _:
            raise ValueError(side)
    ifs.rtde_control.moveJ_IK(next_pos, speed=0.5)
    bucket_manip.place_bucket(ifs)
    if side == "right":
        rotvec = [0, -exportde.pi, 0]
    else:
        rotvec = [exportde.pi, 0, 0]
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    tcp_pos = tcp_pos[:3] + rotvec
    ifs.rtde_control.moveL(tcp_pos)
    movements.fold(ifs)


@exportde.expo_handler
def load(ifs: exportde.RobotInterfaces, side: exportde.Side) -> None:
    SAFE_HEIGHT = 0.3

    movements.unfold(ifs)
    bucket_pos = _get_bucket_position(0.2, side)
    move = bucket_pos.copy()
    move[2] = SAFE_HEIGHT
    ifs.rtde_control.moveJ_IK(move)
    bucket_manip.pick_bucket(ifs, bucket_pos)
    ifs.rtde_control.moveL(move)
    center = _get_bucket_position(exportde.BUCKET_HEIGHT, "center")
    center[:2] = exportde.BUCKET_POSITION_XY
    ifs.rtde_control.moveL(center)
    bucket_manip.place_bucket(ifs)
    movements.fold(ifs)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Specify a side: left or right.")
        exit(1)
    side = sys.argv[1]
    if side not in ["left", "right"]:
        print("Wrong argument: ", side)
        exit(1)
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        disload(ifs, side=side)
