"""Here are listed hardcoded variables."""
import numpy as np

pi = np.pi
hpi = np.pi / 2

HOST = "192.168.1.179"
HOME_POSITION_J = (0, -1.047153727417328, 7 * np.pi / 8, 0., -hpi, 0)
FOLD_POSITION_J = (0, -1.15, 2.7, -pi, hpi, 0)
UNFOLD_POSITION_J = (0, -hpi, hpi, -hpi, -hpi, 0)
BUCKET_POSITION_L = (-0.46, 0, 0.2, 0.973, 1.4, -1.35)

GRIPPER_MASS = 0.925
GRIPPER_COG = (0, 0, 0.058)
BUCKET_MASS = 3.
BUCKET_COG = (0, 0, 0.14 + 0.15)  # gripper len + bucket height
