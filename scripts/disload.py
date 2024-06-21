import time

import exportde
import movements
import bucket_manip


@exportde.expo_handler
def disload(ifs: exportde.RobotInterfaces) -> None:
    movements.unfold(ifs)
    ifs.rtde_control.moveJ(exportde.UNFOLD_POSITION_J)
    bucket_manip.pick_bucket(ifs)
    pos = ifs.rtde_receive.getActualTCPPose()
    pos[2] += 0.2
    ifs.rtde_control.moveL(pos)
    time.sleep(2.)
    bucket_manip.place_bucket(ifs)
    movements.fold(ifs)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        disload(ifs)
