import time
import logging

from dashboard_client import DashboardClient
from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface

from exportde import exceptions
from exportde.robotiq_gripper import RobotiqGripper


_log = logging.getLogger(__name__)


class RobotInterfaces:
    __slots__ = (
        '_dashboard',
        '_rtde_c',
        '_rtde_r',
        '_gripper'
    )

    def __init__(
            self,
            host: str,
            ur_cap_port: int = 50002,
            frequency: float = -1.0,
            gripper_port: int = 63352
            ) -> None:
        dashboard = DashboardClient(host)
        dashboard.connect()
        if not dashboard.isInRemoteControl():
            raise exceptions.PolyscopeException('Remote control must be set.')

        rtde_r = RTDEReceiveInterface(host, frequency=frequency)
        flags = RTDEControlInterface.FLAG_USE_EXT_UR_CAP
        flags |= RTDEControlInterface.FLAG_UPLOAD_SCRIPT
        rtde_c = RTDEControlInterface(
            host,
            frequency=frequency,
            flags=flags,
            ur_cap_port=ur_cap_port
        )
        gripper = RobotiqGripper()
        gripper.connect(host, gripper_port)
        if not gripper.is_active():
            gripper.activate(auto_calibrate=False)

        self._dashboard = dashboard
        self._rtde_c = rtde_c
        self._rtde_r = rtde_r
        self._gripper = gripper

    def __enter__(self) -> 'RobotInterfaces':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            _log.error('Protective stop triggered by user')
            self._rtde_c.triggerProtectiveStop()

        time.sleep(0.1)
        self.handle_safety()
        self.disconnect()

    def handle_safety(self) -> bool:
        safety_mode = self._rtde_r.getSafetyMode()
        match safety_mode:
            case 0 | 1:  # normal or reduced 
                return True
            case 3:  # protective stop
                _log.info('Protective stop lifted')
                time.sleep(5.1)  # 5 secs required to pass
                self._dashboard.closeSafetyPopup()
                self._dashboard.unlockProtectiveStop()
                self._rtde_c.reuploadScript()
                return True
            case _:
                return False

    def disconnect(self):
        self._rtde_c.stopScript()
        self._rtde_c.disconnect()
        self._gripper.disconnect()
        self._rtde_r.disconnect()
        self._dashboard.disconnect()

    @property
    def dashboard_client(self) -> DashboardClient:
        return self._dashboard

    @property
    def rtde_control(self) -> RTDEControlInterface:
        if not self._rtde_c.isConnected():
            _log.error('RTDEC access when disconnected')
            raise exceptions.RTDEControlException('Not connected')
        if not self._rtde_c.isProgramRunning():
            _log.error('RTDEC accessed when program is not running')
            raise exceptions.RTDEControlException('Program is not running')
        return self._rtde_c
    
    @property
    def rtde_receive(self) -> RTDEReceiveInterface:
        return self._rtde_r

    @property
    def robotiq_gripper(self) -> RobotiqGripper:
        return self._gripper
