import time
import exportde
from disload import load, disload


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Specify a side: left or right")
        exit(1)
    side = sys.argv[1]
    if side not in ("left", "right"):
        print("Unknown side: ", side)
        exit(1)
    wait_for = 2.0
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        while True:
            last_known_bucket_pos = disload(ifs, side=side)
            time.sleep(wait_for)
            load(ifs, side=side, last_known_bucket_pos=last_known_bucket_pos)
            time.sleep(wait_for)
