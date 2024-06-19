import numpy as np

import exportde
from safe_home import safe_home
from bucket_manip import pick_bucket, place_bucket


@exportde.expo_handler
def disload(ifs: exportde.RobotInterfaces) -> None:
    safe_home(ifs)
    ifs.rtde_control.moveJ(exportde.BEGIN_POSITION_J)
    pick_bucket(ifs)
    # ifs.rtde_control.setPayload()
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    tcp_pos[2] += .1
    ifs.rtde_control.moveL(tcp_pos)
    joint_pos = ifs.rtde_receive.getActualQ()
    joint_pos[0] += np.pi / 2
    ifs.gripper.move(position=0, speed=255, force=255)
    place_bucket(ifs)
    safe_home(ifs)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        disload(ifs)
