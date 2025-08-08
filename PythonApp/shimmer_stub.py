"""Stub implementations used when the optional ``pyshimmer`` package is missing."""


class Serial:
    def __init__(self, *args, **kwargs):
        pass


class ShimmerBluetooth:
    def __init__(self, *args, **kwargs):
        pass


class DataPacket:
    def __init__(self, *args, **kwargs):
        pass


DEFAULT_BAUDRATE = 115200
