"""Here are listed hardcoded variables."""
from typing import Literal, List
import numpy as np

Side = Literal["left", "right"]
Position = List[float]

pi = np.pi
hpi = np.pi / 2

HOST = "192.168.1.179"
#FOLD_POSITION_J = (-hpi, -hpi, np.deg2rad(160), -pi, hpi, -pi)  # TODO: change base rotation
#UNFOLD_POSITION_J = (-hpi, -hpi, hpi, 0.8 * hpi, hpi, -pi)
FOLD_POSITION_J = (0, -hpi, -np.deg2rad(160), 0, -hpi, -pi) 
UNFOLD_POSITION_J = (0, -hpi, -hpi, np.deg2rad(-250), -hpi, -pi)
UNFOLD_POSITION_J = (0, -80, -70, -270, -90, -180)
UNFOLD_POSITION_J = tuple(map(np.deg2rad, UNFOLD_POSITION_J))
TRANSPORTING_POSITION_J = (-270, 0, -164, -102, -176, 270)
TRANSPORTING_POSITION_J = tuple(map(np.deg2rad, TRANSPORTING_POSITION_J))

MOVEL_SPEED = 0.1  # m/s
MOVEL_ACCELERATION = 0.6  # m/s^2
MOVEJ_SPEED = 0.7  # rad/s
MOVEJ_ACCELERATION = 0.8  # rad/s^2

PLATFORM_HEIGHT = 0.559
PLATFORM_HALFWIDTH = 0.630 / 2 + 0.2
SAFE_HEIGHT = 0.  # robot_base
PEDESTAL_HEIGHT = 0.06
GRASP_OFFSET = 0.12

GRIPPER_LEN = 0.1493
GRIPPER_MASS = 0.925
GRIPPER_COG = (0, 0, 0.058)

BUCKET_HEIGHT = 0.33
BUCKET_POSITION_XY = (-0.436, -0.016)
BUCKET_MASS = 3.
BUCKET_COG = (0, 0, 0.14 + 0.15)  # gripper len + bucket height
