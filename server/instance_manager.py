from typing import List, Optional
from permission.permission_manager import PermissionManager
from .instance import ServerInstance
from .controllers.instance_api_controller import InstanceApiController
from database_utils.database import Database
from .instance_loader import InstanceLoader
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from server.controllers.instance_manager_controller import InstanceManagerController


KSM_DATABASE = "ksm_database"


class InstanceManager(Database, InstanceManagerController):
    __instances: List[ServerInstance]
    __permission_manager: PermissionManager
    __instance_folder: str
    __instance_api: InstanceApiController

    def __init__(self, instance_api: InstanceApiController, *args, **kwargs):
        self.__instance_api = instance_api

        super().__init__(*args, **kwargs)

    def __load_instance(
            self,
            instance_id: int,
            instance_name: str,
            instance_cmd: str,
            instance_folder: str
    ) -> ServerInstance:
        instance_arguments = self.__instance_api.instance_arguments.get_arguments(instance_id)

        print(instance_arguments)

        instance = ServerInstance(
            self.__permission_manager,
            instance_id,
            instance_name,
            instance_cmd,
            instance_arguments,
            instance_folder
        )
        self.__instances.append(instance)

        return instance

    def __generate_folder(self, instance_name: str) -> str:
        return f"{self.__instance_folder}{instance_name}/"

    def get_instance_by_id(self, instance_id: int) -> Optional[ServerInstance]:
        for instance in self.__instances:
            if instance.instance_id == instance_id:
                return instance

    def start(self):
        self.__instances = []
        self._connect(KSM_DATABASE)

        self._cursor.execute("CREATE TABLE IF NOT EXISTS instances ("
                             "instance_id INT PRIMARY KEY AUTO_INCREMENT,"
                             "name CHAR(128) UNIQUE,"
                             "folder_name CHAR(128) UNIQUE,"
                             "cmd CHAR(128)"
                             ")")

    def create_instance(self, name: str, instance_type: str):
        if not (self._connector and self._cursor):
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Database doesn't exist.")
                    .build())

        instance_loader = InstanceLoader(self.__instance_folder, name, instance_type)
        status = instance_loader.start()
        if not status:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Invalid parameters!")
                    .build())

        instance_loader.load()

        self._connect(KSM_DATABASE)

        self._cursor.execute("INSERT INTO instances (name) VALUES (%s)", (name, ))
        self._connector.commit()
        self._cursor.execute("SELECT instance_id FROM instances WHERE name = %s", (name, ))
        instance_id = self._cursor.fetchone()[0]
        instance_folder = self.__generate_folder(name)

        self.__load_instance(instance_id, name, instance_folder)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Instance created!").build()

    def load_folder(self, instance_folder: str):
        self.__instance_folder = instance_folder

    def load_permission_manager(self, permission_manager: PermissionManager):
        self.__permission_manager = permission_manager

    def load_instances(self):
        self._connect(KSM_DATABASE)

        self._cursor.execute("SELECT * FROM instances")
        instances = self._cursor.fetchall()

        for instance_data in instances:
            instance_id = instance_data[0]
            instance_name = instance_data[1]
            instance_folder_name = instance_data[2]
            instance_cmd = instance_data[3]
            instance_folder = self.__generate_folder(instance_folder_name)

            self.__load_instance(instance_id, instance_name, instance_cmd, instance_folder)

    @property
    def instances(self) -> List[ServerInstance]:
        return self.__instances
