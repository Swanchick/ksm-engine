from typing import List
from api.base_caller import BaseCaller
from .instance_callback import InstanceCallback
from server.permission.permission_manager import PermissionManager
from server.permission.permissions import Permissions
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus


class InstanceBaseCaller(BaseCaller):
    __instance_id: int
    _permission_manager: PermissionManager

    registered_callbacks: List[InstanceCallback] = []

    def __init__(self, class_instance, instance_id: int, permission_manager: PermissionManager):
        self._permission_manager = permission_manager
        self.__instance_id = instance_id

        super().__init__(class_instance)

    @classmethod
    def register(cls, name: str, *args, **kwargs):
        if len(args) == 0:
            return

        permission = args[0]
        if not isinstance(permission, Permissions):
            return

        def decorator(func: callable):
            callback = InstanceCallback(name, func, permission)
            cls.registered_callbacks.append(callback)

            return func

        return decorator

    def __check_permission(self, user_id: int, instance_id: int, permission: Permissions) -> bool:
        return self._permission_manager.check_permission(user_id, instance_id, permission)

    def call(self, name: str, user_id: int, *args):
        for callback in self.registered_callbacks:
            if callback.name == name:
                if not self.__check_permission(user_id, self.__instance_id, callback.permission):
                    return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()
                try:
                    response = callback.call(self._class_instance, *args)
                except Exception as e:
                    return (ResponseBuilder()
                            .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                            .message(str(e))
                            .build())
                else:
                    return response
