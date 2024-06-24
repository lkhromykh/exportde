import exportde
from exportde.exceptions import FailedGraspException, ArmMoveException

import movements
import bucket_manip


@exportde.expo_handler
def disload(ifs: exportde.RobotInterfaces, side: exportde.Side) -> None:
    movements.unfold(ifs)
    bucket_manip.pick_bucket(ifs)
    pos = ifs.rtde_receive.getActualTCPPose()
    pos[2] += 0.05
    ifs.rtde_control.moveL(pos)
    height = ifs.rtde_receive.getActualTCPPose()[2]
    match side:
        case "right":
            next_pos = [0., -exportde.PLATFORM_HALFWIDTH, height, 0, exportde.hpi, 0]
        case "left":
            next_pos = [-0.2, exportde.PLATFORM_HALFWIDTH, height, 2.221, 0, -2.221]
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("invoke specify a side: left or right.")
        exit(1)
    side = sys.argv[1]
    if side not in ["left", "right"]:
        print("Wrong argument: ", side)
        exit(1)
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        disload(ifs, side=side)
