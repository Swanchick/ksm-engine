from api.callback import Callback
from permission.permissions import Permissions


class InstanceCallback(Callback):
    __permission: Permissions

    def __init__(self, name: str, callback: callable, permission: Permissions):
        self.__permission = permission

        super().__init__(name, callback)

    @property
    def permission(self):
        return self.__permission
