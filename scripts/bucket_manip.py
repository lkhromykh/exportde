import numpy as np
import exportde

HANDLE_POSITION_L = (-0.46, 0., 0.2, 0.973, 1.4, -1.35)


@exportde.expo_handler
def pick_bucket(ifs: exportde.RobotInterfaces) -> None:
    premove = list(HANDLE_POSITION_L)
    premove[1] += 0.1
    ifs.rtde_control.moveL(premove, speed=0.1)
    ifs.gripper.move_and_wait_for_pos(0)
    ifs.rtde_control.moveL(HANDLE_POSITION_L)
    _, status = ifs.gripper.move_and_wait_for_pos(255)
    # assert status == ifs.gripper.ObjectStatus.STOPPED_INNER_OBJECT
    # ifs.rtde_control.setPayload()


@exportde.expo_handler
def place_bucket(ifs: exportde.RobotInterfaces) -> None:
    speed = [0, 0, -0.1, 0, 0, 0]
    direction = [0, 0, -1., 0, 0, 0]
    acceleration = 0.2
    ifs.rtde_control.moveUntilContact(speed, direction, acceleration)
    _, status = ifs.gripper.move_and_wait_for_pos(0)
    assert status == ifs.gripper.ObjectStatus.AT_DEST
    # ifs.rtde_control.setPayload()
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    tcp_pos = tcp_pos[:3] + [2.2, 2.2, 0]
    ifs.rtde_control.moveL(tcp_pos)


def _CoG(mass: list[float], distance: list[np.ndarray]) -> np.ndarray:
    # Payload center of gravity configuration should be updated after a grasp.
    assert len(mass) == len(distance)
    cog = np.zeros(3)
    for m, d in zip(mass, distance):
        cog += m * d
    return cog / sum(mass)


if __name__ == "__main__":
   with exportde.RobotInterfaces(exportde.HOST) as ifs:
       pick_bucket(ifs)
