import numpy as np
import exportde

JOINT_TOLERANCE = 0.01
SAFE_HEIGHT = 0.0


@exportde.expo_handler
def unfold(ifs: exportde.RobotInterfaces) -> None:
    """Move to the working position above a platform."""
    ifs.gripper.move(0)
    cur_joints = ifs.rtde_receive.getActualQ()
    if np.allclose(cur_joints, exportde.UNFOLD_POSITION_J, atol=JOINT_TOLERANCE):
        return

    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    if tcp_pos[2] < SAFE_HEIGHT:
        tcp_pos[2] = SAFE_HEIGHT
        ifs.rtde_control.moveL(tcp_pos)
    ifs.rtde_control.moveJ(exportde.UNFOLD_POSITION_J)


@exportde.expo_handler
def fold(ifs: exportde.RobotInterfaces) -> None:
    """Move to folded position."""
    cur_joint = ifs.rtde_receive.getActualQ()
    if np.allclose(cur_joint, exportde.FOLD_POSITION_J, atol=JOINT_TOLERANCE):
        return
    if not np.allclose(cur_joint, exportde.UNFOLD_POSITION_J, atol=JOINT_TOLERANCE):
        unfold(ifs)
    ifs.gripper.move(255)
    ifs.rtde_control.moveJ(exportde.FOLD_POSITION_J)


if __name__ == "__main__":
    import sys
    known_moves = dict(fold=fold, unfold=unfold)

    if len(sys.argv) != 2:
        print("Specify a move: ", known_moves.keys())
        exit(1)
    move = sys.argv[1]
    if move not in known_moves:
        print("Wrong argument: ", move)
        exit(1)
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        known_moves[move](ifs)
