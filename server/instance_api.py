from typing import Dict, Optional, List
from api import Api, ApiCaller
from .permission.permission_manager import PermissionManager
from .instance import ServerInstance
from .instance_manager import InstanceManager
from .instance_arguments import InstanceArguments
from .instances_call import InstancesCall
from .controllers.instance_api_controller import InstanceApiController


class InstanceApi(Api, InstanceApiController):
    __instances: List[ServerInstance]

    __instance_folder: str
    __instance_manager: InstanceManager
    __instance_arguments: InstanceArguments
    __instances_call: InstancesCall

    def __init__(self, instance_folder: str):
        self.__instance_folder = instance_folder

        self._caller = ApiCaller()

        self.__permission_manager = PermissionManager()

        self.__instance_manager = InstanceManager(self.__instance_folder, self.__permission_manager, self)
        self._caller.register("manager", self.__instance_manager)

        self.__instances_call = InstancesCall(self.__permission_manager, self.__instance_manager)
        self._caller.register("call", self.__instances_call)

        self.__instance_arguments = InstanceArguments()
        self._caller.register("arguments", self.__instance_arguments)

        self.__instance_manager.load_instances()

    def request(self, routes: List[str], *args, **kwargs) -> Dict:
        response = self._caller.request(routes, *args, **kwargs)

        return response

    @property
    def instance_manager(self) -> InstanceManager:
        return self.__instance_manager

    @property
    def instance_arguments(self) -> InstanceArguments:
        return self.__instance_arguments
