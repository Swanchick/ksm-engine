from abc import ABC
from typing import List
from .callback import Callback
from permission.permission_manager import PermissionManager
from permission.permissions import Permissions
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus

REGISTERED_CALLBACKS: List[Callback] = []


def register_call(callback_name: str, permission: Permissions):
    def decorator(func: callable):
        callback = Callback(callback_name, func, permission)
        REGISTERED_CALLBACKS.append(callback)

        return func

    return decorator


class InstanceCaller(ABC):
    __class_instance: type
    __instance_id: int
    _permission_manager: PermissionManager

    def __init__(self, class_instance, instance_id: int, permission_manager: PermissionManager):
        self._callbacks = []
        self._permission_manager = permission_manager
        self.__instance_id = instance_id
        self.__class_instance = class_instance

        super().__init__()

    def __check_permission(self, user_id: int, instance_id: int, permission: Permissions) -> bool:
        return self._permission_manager.check_permission(user_id, instance_id, permission)

    def call(self, name: str, user_id: int, *args, **kwargs):
        for callback in REGISTERED_CALLBACKS:
            if callback.name == name:
                if not self.__check_permission(user_id, self.__instance_id, callback.permission):
                    return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

                try:
                    return callback.call(self.__class_instance, *args, **kwargs)
                except Exception as e:
                    return (ResponseBuilder()
                            .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                            .message(str(e))
                            .build())