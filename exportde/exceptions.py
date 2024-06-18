"""Module exceptions."""


class ExpoException(Exception):
    """Serves as a base class."""


class ProtectiveStop(ExpoException):
    """Protective stop is triggered."""


class ConnectionLost(ExpoException):
    """When WiFi connection drops."""
