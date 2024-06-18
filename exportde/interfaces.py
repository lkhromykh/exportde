"""Interfaces to interact with a UR5e."""
import time
from typing import Self

from dashboard_client import DashboardClient
from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface

from exportde import exceptions
from exportde.robotiq_gripper import RobotiqGripper

__all__ = ("RobotInterfaces",)


class RobotInterfaces:

    __slots__ = ("dashboard_client", "rtde_control", "rtde_receive", "gripper")

    def __init__(self,
                 host: str,
                 ur_cap_port: int = 50002,
                 frequency: float = -1.,
                 gripper_port: int = 63352,
                 ) -> None:
        dashboard_client = DashboardClient(host, verbose=True)
        dashboard_client.connect()
        # assert dashboard_client.isInRemoteControl(), "Remote control mode must be set."
        rtde_receive = RTDEReceiveInterface(host, frequency=frequency)
        flags = RTDEControlInterface.FLAG_USE_EXT_UR_CAP
        flags |= RTDEControlInterface.FLAG_UPLOAD_SCRIPT
        flags |= RTDEControlInterface.FLAG_VERBOSE
        rtde_control = RTDEControlInterface(host, frequency=frequency, flags=flags, ur_cap_port=ur_cap_port)
        gripper = RobotiqGripper()
        gripper.connect(host, gripper_port)
        gripper.activate(auto_calibrate=False)

        self.dashboard_client = dashboard_client
        self.rtde_control = rtde_control
        self.rtde_receive = rtde_receive
        self.gripper = gripper

    def __enter__(self) -> Self:
        # After the following checks robot state can be considered healthy.
        assert self.dashboard_client.isConnected()
        assert self.rtde_receive.isConnected()
        assert self.rtde_control.isConnected()
        assert self.rtde_control.isProgramRunning()
        # assert self.gripper.is_active()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        is_handled = False
        if exc_type is not None:
            if issubclass(exc_type, KeyboardInterrupt):
                is_handled = True
            if issubclass(exc_type, exceptions.ProtectiveStop):
                self.unlock_protective_stop()
        self.disconnect()
        return is_handled

    def disconnect(self) -> None:
        self.rtde_control.stopScript()
        self.rtde_control.disconnect()
        self.rtde_receive.disconnect()
        self.gripper.disconnect()
        self.dashboard_client.disconnect()

    def unlock_protective_stop(self) -> None:
        print("Unlocking protective stop, don't Ctrl+C yet.")
        time.sleep(5.1)
        self.dashboard_client.closeSafetyPopup()
        self.dashboard_client.unlockProtectiveStop()
