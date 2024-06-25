"""Here are listed hardcoded variables."""
from typing import Literal
import numpy as np

type Side = Literal["left", "right"]
type Position = list[float]

pi = np.pi
hpi = np.pi / 2

HOST = "192.168.1.179"
FOLD_POSITION_J = (0, -1.15, 2.7, -pi, hpi, 0)
UNFOLD_POSITION_J = [-0.272, -1.54044, 1.1367, -1.1684241157821198, -1.5707, -0.272]

MOVEL_SPEED = 0.2  # m/s
MOVEL_ACCELERATION = 0.6  # m/s^2
MOVEJ_SPEED = 0.7  # rad/s
MOVEJ_ACCELERATION = 0.8  # rad/s^2

PLATFORM_HEIGHT = 0.243 + 0.451
PLATFORM_HALFWIDTH = 0.60  # 0.537 / 2 + bucket offset
SAFE_HEIGHT = 0.  # robot_base
PEDESTAL_HEIGHT = 0.06
GRASP_OFFSET = 0.15

GRIPPER_LEN = 0.1493
GRIPPER_MASS = 0.925
GRIPPER_COG = (0, 0, 0.058)

BUCKET_HEIGHT = 0.33
BUCKET_POSITION_XY = (-0.436, 0.0072)
BUCKET_MASS = 3.
BUCKET_COG = (0, 0, 0.14 + 0.15)  # gripper len + bucket height
