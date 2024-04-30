from permission import Permissions


class Callback:
    __name: str
    __permission: Permissions
    __instance_id: int
    _callback: callable

    def __init__(self, name: str, callback: callable, instance_id: int, permission: Permissions):
        self.__name = name
        self._callback = callback
        self.__permission = permission
        self.__instance_id = instance_id

    def call(self, *args, **kwargs):
        return self._callback(*args, **kwargs)

    @property
    def name(self):
        return self.__name

    @property
    def instance_id(self) -> int:
        return self.__instance_id

    @property
    def permission(self) -> Permissions:
        return self.__permission
