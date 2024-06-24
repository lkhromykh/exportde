"""For specific exceptions handling."""


class ExpoException(Exception):
    """Base class for all exceptions."""


class ArmMoveException(ExpoException):
    """Arm move command exception."""


class FailedGraspException(ExpoException):
    """Unsuccessful grasp exception."""
