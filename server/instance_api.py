from typing import Dict, Optional, List
from api.api import Api
from .permission.permission_manager import PermissionManager
from .instance import ServerInstance
from .instance_manager import InstanceManager
from .instance_arguments import InstanceArguments
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from .controllers.instance_api_controller import InstanceApiController
from user.user import User


class InstanceApi(Api, InstanceApiController):
    __instances: List[ServerInstance]

    __instance_folder: str
    __instance_manager: InstanceManager
    __instance_arguments: InstanceArguments

    __permission_manager: PermissionManager

    def __init__(self, instance_folder: str):
        self.__instance_folder = instance_folder

        self.__instance_manager = InstanceManager(self)
        self.__instance_manager.load_folder(self.__instance_folder)
        self.__instance_manager.start()

        self.__instance_arguments = InstanceArguments()
        self.__instance_arguments.start()

    def request(self, routes: List[str]) -> Dict:
        pass

    @property
    def instance_manager(self) -> InstanceManager:
        return self.__instance_manager

    @property
    def instance_arguments(self) -> InstanceArguments:
        return self.__instance_arguments
