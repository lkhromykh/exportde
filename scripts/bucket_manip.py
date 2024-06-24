import time

import numpy as np
from scipy.spatial.transform import Rotation

import exportde
from exportde.exceptions import FailedGraspException, ArmMoveException


def _get_payload_params(mass: list[float], distance: list[np.ndarray]) -> tuple[float, np.ndarray]:
    return exportde.GRIPPER_MASS, exportde.GRIPPER_COG
    # Payload configuration should be updated on grasp.
    assert len(mass) == len(distance)
    cog = np.zeros(3)
    for m, d in zip(mass, distance):
        cog += m * np.asarray(d)
    payload = sum(mass)
    return payload, cog / payload


@exportde.expo_handler
def pick_bucket(ifs: exportde.RobotInterfaces, bucket_pos: exportde.Position) -> None:
    ifs.gripper.move(0)
    pos, rotvec = np.split(np.asarray(bucket_pos), 2)
    rot = Rotation.from_rotvec(rotvec)
    premove = rot.apply([0, 0, -0.15])
    premove += pos
    premove = np.concatenate([premove, rotvec])
    breakpoint()
    ifs.rtde_control.moveL(premove)
    ifs.rtde_control.moveL(bucket_pos, asynchronous=True)
    _, status = ifs.gripper.move_and_wait_for_pos(255, speed=140, force=0)
    if status != ifs.gripper.ObjectStatus.STOPPED_INNER_OBJECT:
        exportde.get_logger().info("Object was not detected by the gripper.")
        # raise FailedGraspException("Unsuccessful grasp. Resetting position.")
    exit()  # testing w/o premove
    payload, cog = _get_payload_params(
        [exportde.GRIPPER_MASS, exportde.BUCKET_MASS],
        [exportde.GRIPPER_COG, exportde.BUCKET_COG]
    )
    ifs.rtde_control.setPayload(payload, cog)
    exportde.get_logger().debug("Updated payload: %s, %s",
                               ifs.rtde_receive.getPayloadCog(), ifs.rtde_receive.getPayload())
    pos = ifs.rtde_receive.getActualTCPPose()
    pos[2] += 0.05
    ifs.rtde_control.moveL(pos)


@exportde.expo_handler
def place_bucket(ifs: exportde.RobotInterfaces) -> None:
    speed = [0, 0, -0.2, 0, 0, 0]
    direction = [0, 0, -1., 0, 0, 0]
    acceleration = 0.2
    if ifs.rtde_control.toolContact(direction) > 1:
        exportde.get_logger().info("Contact is detected prior to move.")
        raise ArmMoveException("Contact is detected prior to move.")
    ifs.rtde_control.moveUntilContact(speed, direction, acceleration)
    exportde.get_logger().info("Bucket was left at: %s", ifs.rtde_receive.getActualTCPPose())
    _, status = ifs.gripper.move_and_wait_for_pos(0)
    ifs.rtde_control.setPayload(exportde.GRIPPER_MASS, exportde.GRIPPER_COG)
    time.sleep(0.05)
    exportde.get_logger().debug("Updated payload: %s, %s",
                               ifs.rtde_receive.getPayloadCog(), ifs.rtde_receive.getPayload())

    if status != ifs.gripper.ObjectStatus.AT_DEST:
        raise FailedGraspException("Something preventing gripper from opening.")


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        pick_bucket(ifs)
        # place_bucket(ifs)
