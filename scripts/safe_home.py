import numpy as np
import exportde


@exportde.expo_handler
def safe_home(ifs: exportde.RobotInterfaces, safe_height: float = 0.3) -> None:
    ifs.gripper.move_and_wait_for_pos(255)
    cur_joints = ifs.rtde_receive.getActualQ()
    if np.allclose(cur_joints, exportde.HOME_POSITION_J):
        return

    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    if tcp_pos[2] < safe_height:
        tcp_pos[2] = safe_height
        ifs.rtde_control.moveL(tcp_pos)
    ifs.rtde_control.moveJ(exportde.HOME_POSITION_J)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        safe_home(ifs)
