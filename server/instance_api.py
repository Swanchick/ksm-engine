from typing import Dict, Optional, List
from api.api import Api
from permission.permission_manager import PermissionManager
from .instance import ServerInstance
from .instance_manager import InstanceManager
from .instance_arguments import InstanceArguments
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from .controllers.instance_api_controller import InstanceApiController


class InstanceApi(Api, InstanceApiController):
    __instances: List[ServerInstance]

    __instance_folder: str
    __instance_manager: InstanceManager
    __instance_arguments: InstanceArguments

    __permission_manager: PermissionManager

    def __init__(self, instance_folder: str):
        self.__instance_folder = instance_folder

        self.__instance_arguments = InstanceArguments()
        self.__instance_arguments.start()

        self.__instance_manager = InstanceManager(self)
        self.__instance_manager.load_folder(self.__instance_folder)
        self.__instance_manager.start()

    def request(self, method_name: str, instance_data: Dict) -> Optional[Dict]:
        instance_id = int(instance_data["instance_id"])
        instance = self.__instance_manager.get_instance_by_id(instance_id)

        if instance is None:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Instance not found")
                    .build())

        args = instance_data["args"] if "args" in instance_data else []

        output_data = instance.call(
            method_name, instance_data["user_id"], *args)

        return output_data

    @property
    def instance_manager(self) -> InstanceManager:
        return self.__instance_manager

    @property
    def instance_arguments(self) -> InstanceArguments:
        return self.__instance_arguments
