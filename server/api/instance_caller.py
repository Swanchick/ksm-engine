from typing import List, Type
from api import BaseCaller, Api, api_data
from .instance_callback import InstanceCallback
from server.permission.permission_manager import PermissionManager
from server.permission.permissions import Permissions
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from user.user import User


class InstanceCaller(BaseCaller):
    __permission_manager: PermissionManager
    __api: Api

    instance_callbacks: List[InstanceCallback] = []

    def __init__(self, permission_manager: PermissionManager):
        self.__permission_manager = permission_manager

    def get(self, name: str):
        pass

    @classmethod
    def register(cls, name: str, permission: Permissions = None, *args, **kwargs) -> callable:
        if permission is None:
            return

        def decorator(func: callable):
            callback = InstanceCallback(name, func, permission)
            cls.instance_callbacks.append(callback)

            return func

        return decorator

    def __check_permission(self, user: User, instance_id: int, permission: Permissions) -> bool:
        return self.__permission_manager.check_permission(user, instance_id, permission)

    def request(self, routes: List[str], instance: Type = None, *args):
        if len(routes) != 1:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        name = routes[0]

        data = api_data.get("data")
        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        instance_id = data.get("instance_id")
        args = data.get("args")
        if instance_id is None or args is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        user = api_data.get("user")
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        for callback in self.instance_callbacks:
            if callback.name == name:
                if not self.__check_permission(user, instance_id, callback.permission):
                    return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

                try:
                    response = callback.request(self.instance_callbacks, *args)
                except Exception as e:
                    return (ResponseBuilder()
                            .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                            .message(str(e))
                            .build())
                else:
                    return response
