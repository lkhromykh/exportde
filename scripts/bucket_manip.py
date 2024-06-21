import time

import numpy as np
import exportde


def _get_payload_params(mass: list[float], distance: list[np.ndarray]) -> tuple[float, np.ndarray]:
    # Payload center of gravity configuration should be updated after a grasp.
    assert len(mass) == len(distance)
    cog = np.zeros(3)
    for m, d in zip(mass, distance):
        cog += m * np.asarray(d)
    payload = sum(mass)
    return payload, cog / payload


@exportde.expo_handler
def pick_bucket(ifs: exportde.RobotInterfaces) -> None:
    ifs.gripper.move(0)
    premove = list(exportde.BUCKET_POSITION_L)
    premove[1] += 0.13
    ifs.rtde_control.moveL(premove, speed=0.1)
    ifs.rtde_control.moveL(exportde.BUCKET_POSITION_L, asynchronous=True)
    _, status = ifs.gripper.move_and_wait_for_pos(255, speed=140, force=0)
    if status != ifs.gripper.ObjectStatus.STOPPED_INNER_OBJECT:
        ifs.rtde_control.moveJ(exportde.UNFOLD_POSITION_J)
        raise RuntimeError("Unsuccessful grasp. Resetting position.")
    payload, cog = _get_payload_params(
        [exportde.GRIPPER_MASS, exportde.BUCKET_MASS],
        [exportde.GRIPPER_COG, exportde.BUCKET_COG]
    )
    ifs.rtde_control.setPayload(payload, cog)
    print("Updated params: ", ifs.rtde_receive.getPayloadCog(), ifs.rtde_receive.getPayload())


@exportde.expo_handler
def place_bucket(ifs: exportde.RobotInterfaces) -> None:
    speed = [0, 0, -0.1, 0, 0, 0]
    direction = [0, 0, -1., 0, 0, 0]
    acceleration = 0.2
    ifs.rtde_control.moveUntilContact(speed, direction, acceleration)
    _, status = ifs.gripper.move_and_wait_for_pos(100)
    ifs.rtde_control.setPayload(exportde.GRIPPER_MASS, exportde.GRIPPER_COG)
    time.sleep(0.05)
    print("Updated params: ", ifs.rtde_receive.getPayloadCog(), ifs.rtde_receive.getPayload())
    if status != ifs.gripper.ObjectStatus.AT_DEST:
        raise RuntimeError("Something is already detected")
    tcp_pos = ifs.rtde_receive.getActualTCPPose()
    tcp_pos = tcp_pos[:3] + [2.2, 2.2, 0]
    ifs.rtde_control.moveL(tcp_pos)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        pick_bucket(ifs)
        # place_bucket(ifs)
