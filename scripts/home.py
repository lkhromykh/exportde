import exportde


@exportde.expo_handler()
def home(ifs: exportde.RobotInterfaces) -> None:
    ifs.rtde_control.moveJ(exportde.SAFE_JOINT_POSITION)


if __name__ == "__main__":
    with exportde.RobotInterfaces(exportde.HOST) as ifs:
        home(ifs)
