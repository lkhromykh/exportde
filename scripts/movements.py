import numpy as np
import exportde


@exportde.expo_handler
def fold(ifs: exportde.RobotInterfaces) -> None:
    cur_joint = ifs.rtde_receive.getActualQ()
    if np.allclose(cur_joint, exportde.FOLD_POSITION_J, atol=0.02):
        return
    if not np.allclose(cur_joint, exportde.UNFOLD_POSITION_J, atol=0.02):
        ifs.rtde_control.moveJ(exportde.UNFOLD_POSITION_J)
    ifs.rtde_control.moveJ(exportde.FOLD_POSITION_J)


@exportde.expo_handler
def unfold(ifs: exportde.RobotInterfaces, safe_height: float = 0.0) -> None:
    cur_joints = ifs.rtde_receive.getActualQ()
    if np.allclose(cur_joints, exportde.UNFOLD_POSITION_J, atol=0.02):
        return

    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    if tcp_pos[2] < safe_height:
        tcp_pos[2] = safe_height
        ifs.rtde_control.moveL(tcp_pos)
    ifs.rtde_control.moveJ(exportde.UNFOLD_POSITION_J)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        fold(ifs)
