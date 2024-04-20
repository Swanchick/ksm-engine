from enum import Enum


class Permissions(Enum):
    INSTANCE_VIEW = 1
    INSTANCE_CONSOLE = 2
    INSTANCE_START_STOP = 4
    INSTANCE_SHOW_STATS = 8
    INSTANCE_USER_EDIT = 16
    FILES_SHOW = 32
    FILES_EDIT = 64
    FILES_VIEW = 128
    FILES_CREATE = 256
    