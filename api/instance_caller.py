from abc import ABC
from typing import List
from .callback import Callback
from permission import PermissionManager, Permissions
from utils import ResponseBuilder, HttpStatus


class InstanceCaller(ABC):
    _permission_manager: PermissionManager
    _callbacks: List[Callback]

    def __init__(self, permission_manager: PermissionManager):
        self._callbacks = []
        self._permission_manager = permission_manager

        super().__init__()

    def __is_callback_exists(self, name: str) -> bool:
        for callback in self._callbacks:
            if callback.name == name:
                return True

        return False

    def __check_permission(self, user_id: int, instance_id: int, permission: Permissions) -> bool:
        return self._permission_manager.check_permission(user_id, instance_id, permission)

    def _register(self, name: str, callback: callable, instance_id: int, permission: Permissions):
        callback = Callback(name, callback, instance_id, permission)
        self._callbacks.append(callback)

    def _unregister(self, name: str):
        for callback in self._callbacks:
            if callback.name == name:
                self._callbacks.remove(callback)
                break

    def unregister_all(self):
        self._callbacks = []

    def call(self, name: str, user_id: int, *args, **kwargs):
        for callback in self._callbacks:
            if callback.name == name:
                if not self.__check_permission(user_id, callback.instance_id, callback.permission):
                    return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

                return callback.call(*args, **kwargs)
