from typing import List, Optional, Dict
from api import Api, api_data
from .api.instance_caller import InstanceCaller
from .instance import ServerInstance
from .controllers.instance_manager_controller import InstanceManagerController
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus


class InstancesCall(Api):
    __instances: List[ServerInstance]
    __instance_manager: InstanceManagerController

    def __init__(self, permission_manager, instance_manager):
        super().__init__()

        self.__instance_manager = instance_manager
        self._caller = InstanceCaller(permission_manager)

    def __get_instance(self, instance_id: int) -> Optional[ServerInstance]:
        for instance in self.__instance_manager.instances:
            if instance.instance_id == instance_id:
                return instance

        return

    def request(self, routes: List[str], *args, **kwargs) -> Optional[Dict]:
        user = api_data.get("user")
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        data = api_data.get("data")
        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad Request!").build()

        instance_id = data.get("instance_id")
        if instance_id is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad Request!").build()

        instance = self.__get_instance(instance_id)

        if instance is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Instance not found!").build()

        response = self._caller.request(routes, instance=instance, *args)

        return response
