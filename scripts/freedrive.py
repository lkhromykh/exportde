import exportde


@exportde.expo_handler()
def freedrive(ifs: exportde.RobotInterfaces):
    ifs.rtde_control.teachMode()
    input()
    ifs.rtde_control.endTeachMode()


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        freedrive(ifs)
