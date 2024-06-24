import exportde
from exportde.exceptions import FailedGraspException, ArmMoveException

import movements
import bucket_manip


@exportde.expo_handler
def disload(ifs: exportde.RobotInterfaces, side: exportde.Side) -> None:
    movements.unfold(ifs)
    bucket_manip.pick_bucket(ifs, side=side)
    pos = ifs.rtde_receive.getActualTCPPose()
    pos[2] += 0.05
    ifs.rtde_control.moveL(pos)
    height = ifs.rtde_receive.getActualTCPPose()[2]
    match side:
        case "right":
            next_pos = [0., -exportde.PLATFORM_HALFWIDTH, height, 1.20857904,  1.20863503, -1.20954185]
        case "left":
            next_pos = [0., exportde.PLATFORM_HALFWIDTH, height, -1.21778072, 1.2177243, 1.1853924]
        case _:
            raise ValueError(side)
    ifs.rtde_control.moveJ_IK(next_pos, speed=0.5)
    bucket_manip.place_bucket(ifs)
    movements.fold(ifs)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        disload(ifs, side="right")
