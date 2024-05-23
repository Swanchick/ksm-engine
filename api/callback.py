from permission.permissions import Permissions


class Callback:
    __name: str
    __permission: Permissions
    _callback: callable

    def __init__(self, name: str, callback: callable, permission: Permissions):
        self.__name = name
        self._callback = callback
        self.__permission = permission

    def call(self, *args, **kwargs):
        return self._callback(*args, **kwargs)

    @property
    def name(self):
        return self.__name

    @property
    def permission(self) -> Permissions:
        return self.__permission
