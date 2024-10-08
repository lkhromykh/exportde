import time
from typing import List, Optional, Tuple
import numpy as np
from scipy.spatial.transform import Rotation as R

import exportde
from exportde.exceptions import FailedGraspException, ArmMoveException


def _get_payload_params(mass: List[float], distance: List[np.ndarray]) -> Tuple[float, np.ndarray]:
    # Payload configuration should be updated on grasp.
    assert len(mass) == len(distance)
    cog = np.zeros(3)
    for m, d in zip(mass, distance):
        cog += m * np.asarray(d)
    payload = sum(mass)
    return payload, cog / payload

WBUCKET_PAYLOAD, WBUCKET_COG = _get_payload_params(
    [exportde.GRIPPER_MASS, exportde.BUCKET_MASS],
    [exportde.GRIPPER_COG, exportde.BUCKET_COG]
)
OPEN_GRIPPER_POS = 0


@exportde.expo_handler
def pick_bucket(ifs: exportde.RobotInterfaces, bucket_pos: exportde.Position) -> None:
    ifs.gripper.move(OPEN_GRIPPER_POS)
    pos, rotvec = np.split(np.asarray(bucket_pos), 2)
    premove = R.from_rotvec(rotvec).apply([0, 0, -exportde.GRASP_OFFSET])  # side grasp move
    ifs.rtde_control.moveL(np.r_[pos + premove, rotvec])
    ifs.rtde_control.moveL(bucket_pos, asynchronous=False)
    _, status = ifs.gripper.move_and_wait_for_pos(255, speed=255, force=20)
    if status != ifs.gripper.ObjectStatus.STOPPED_INNER_OBJECT:
        exportde.get_logger().info("Object was not detected by the gripper.")
        raise FailedGraspException("Unsuccessful grasp. Resetting position.")
    ifs.rtde_control.setPayload(WBUCKET_PAYLOAD, WBUCKET_COG)
    time.sleep(0.01)
    exportde.get_logger().debug("Updated payload: %s, %s",
                                ifs.rtde_receive.getPayloadCog(), ifs.rtde_receive.getPayload())


@exportde.expo_handler
def place_bucket(ifs: exportde.RobotInterfaces, height: Optional[float] = None) -> List[float]:
    if height is not None:  # predefined height
        last_known_bucket_pos = ifs.rtde_receive.getActualTCPPose()
        last_known_bucket_pos[2] = height
        ifs.rtde_control.moveL(last_known_bucket_pos)
    else:  # move until contact
        speed = [0, 0, -0.1, 0, 0, 0]
        direction = [0, 0, -1., 0, 0, 0]
        acceleration = 0.2
        if ifs.rtde_control.toolContact(direction) > 1:
            exportde.get_logger().info("Contact is detected prior to move.")
            raise ArmMoveException("Contact is detected prior to move.")
        ifs.rtde_control.moveUntilContact(speed, direction, acceleration)
        last_known_bucket_pos = ifs.rtde_receive.getActualTCPPose()
    exportde.get_logger().info("Bucket was left at: %s", last_known_bucket_pos)
    _, status = ifs.gripper.move_and_wait_for_pos(OPEN_GRIPPER_POS)
    if status != ifs.gripper.ObjectStatus.AT_DEST:
        ifs.gripper.move_and_wait_for_pos(200)
        raise FailedGraspException("Something prevents gripper from opening.")
    ifs.rtde_control.setPayload(exportde.GRIPPER_MASS, exportde.GRIPPER_COG)
    time.sleep(0.01)
    exportde.get_logger().debug("Updated payload: %s, %s",
                                ifs.rtde_receive.getPayloadCog(), ifs.rtde_receive.getPayload())
    return last_known_bucket_pos
