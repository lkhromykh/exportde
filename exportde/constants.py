"""Here are listed hardcoded variables."""
from typing import Literal
import numpy as np

type Side = Literal["left", "right"]
type Position = list[float]

pi = np.pi
hpi = np.pi / 2

HOST = "192.168.1.179"
HOME_POSITION_J = (0, -1.047153727417328, 7 * np.pi / 8, 0., -hpi, 0)
FOLD_POSITION_J = (0, -1.15, 2.7, -pi, hpi, 0)
UNFOLD_POSITION_J = (0, -hpi, hpi, -hpi, -hpi, 0)

PLATFORM_HEIGHT = 0.243 + 0.451
PLATFORM_HALFWIDTH = 0.70  # 0.537 / 2 + bucket offset

GRIPPER_LEN = 0.1493
GRIPPER_MASS = 0.925
GRIPPER_COG = (0, 0, 0.058)
BUCKET_HEIGHT = 0.2  # 0.17 + 0.08
BUCKET_POSITION_XY = (-0.4255, 0)
BUCKET_MASS = 3.
BUCKET_COG = (0, 0, 0.14 + 0.15)  # gripper len + bucket height
