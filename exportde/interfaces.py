"""Interfaces to interact with a UR5e."""
import time
from typing import List

from dashboard_client import DashboardClient
from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface

from exportde.robotiq_gripper import RobotiqGripper
from exportde.logging import expo_handler, get_logger
from exportde import constants

__all__ = ("RobotInterfaces",)


class _RTDEControlInterface(RTDEControlInterface):
    """Overwrite default speed and acceleration and prohibit usage of movePath syntax."""

    def moveL(self, pose: List[float],
              speed=constants.MOVEL_SPEED,
              acceleration=constants.MOVEL_ACCELERATION,
              asynchronous=False
              ) -> bool:
        return super().moveL(pose, speed, acceleration, asynchronous)

    def moveJ_IK(self, pose: List[float],
                 speed=constants.MOVEJ_SPEED,
                 acceleration=constants.MOVEJ_ACCELERATION,
                 asynchronous=False
                 ) -> bool:
        return super().moveJ_IK(pose, speed, acceleration, asynchronous)

    def moveJ(self, pose: List[float],
              speed=constants.MOVEJ_SPEED,
              acceleration=constants.MOVEJ_ACCELERATION,
              asynchronous=False
              ) -> bool:
        return super().moveJ(pose, speed, acceleration, asynchronous)

    def moveL_FK(self, pose: List[float],
                 speed=constants.MOVEL_SPEED,
                 acceleration=constants.MOVEL_ACCELERATION,
                 asynchronous=False
                 ) -> bool:
        return super().moveL_FK(pose, speed, acceleration, asynchronous)


class RobotInterfaces:
    """Handle all the required connections."""

    __slots__ = ("dashboard_client", "rtde_control", "rtde_receive", "gripper")

    def __init__(self,
                 host: str,
                 ur_cap_port: int = 50002,
                 frequency: float = 10.,
                 gripper_port: int = 63352,
                 ) -> None:
        dashboard_client = DashboardClient(host, verbose=True)
        dashboard_client.connect()
        assert dashboard_client.isInRemoteControl(), "Robot should be in remote control."
        rtde_receive = RTDEReceiveInterface(host, frequency=frequency)
        flags = RTDEControlInterface.FLAG_USE_EXT_UR_CAP
        flags |= RTDEControlInterface.FLAG_UPLOAD_SCRIPT
        flags |= RTDEControlInterface.FLAG_VERBOSE
        rtde_control = _RTDEControlInterface(host, frequency=frequency, flags=flags, ur_cap_port=ur_cap_port)
        gripper = RobotiqGripper()
        gripper.connect(host, gripper_port)
        if not gripper.is_active():
            gripper.activate(auto_calibrate=False)

        self.dashboard_client = dashboard_client
        self.rtde_control = rtde_control
        self.rtde_receive = rtde_receive
        self.gripper = gripper

    def __enter__(self):
        self.assert_ready()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        is_handled = False
        if exc_type is not None:
            if issubclass(exc_type, KeyboardInterrupt):
                self.rtde_control.triggerProtectiveStop()
                is_handled = True
        self.rtde_control.setPayload(constants.GRIPPER_MASS, constants.GRIPPER_COG)
        time.sleep(0.1)  # let values update
        if not self.rtde_control.isSteady():
            get_logger().warning("Robot is not steady upon exit.")
        if (safety := self.rtde_receive.getSafetyMode()) != 1:
            get_logger().info("Handling safety mode change: %d.", safety)
            self.handle_safety()
        self.disconnect()
        return is_handled

    def assert_ready(self) -> bool:
        """After the following checks robot's state can be considered healthy."""
        assert self.dashboard_client.isConnected(), "Dashboard client is not connected."
        assert self.rtde_receive.isConnected(), "RTDE Receive is not connected."
        assert not self.rtde_receive.isProtectiveStopped(), "Protective stop."
        assert self.rtde_control.isConnected(), "RTDE Control is not connected."
        assert self.rtde_control.isSteady(), "Robot is not steady."
        assert self.rtde_control.isProgramRunning(), "Program is not running."
        assert self.gripper.is_active(), "Gripper is not active."
        return True

    def disconnect(self) -> None:
        self.rtde_control.stopScript()
        self.rtde_control.disconnect()
        self.rtde_receive.disconnect()
        self.gripper.disconnect()
        self.dashboard_client.disconnect()

    @expo_handler
    def handle_safety(self) -> None:
        sm = self.rtde_receive.getSafetyMode()
        if sm == 3:
            print("Unlocking protective stop, don't Ctrl+C yet.")
            time.sleep(5.1)  # required by UR soft.
            self.dashboard_client.closeSafetyPopup()
            self.dashboard_client.unlockProtectiveStop()
        elif (sm == 6) or (sm == 7):
            print("Robot was emergency stopped. Manual unlock is required.")
        elif (sm == 8):
            print("Violation ?")
