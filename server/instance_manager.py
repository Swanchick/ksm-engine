from typing import List, Optional, Dict
from docker import DockerClient, from_env
from permission.permission_manager import PermissionManager
from .instance import ServerInstance
from .controllers.instance_api_controller import InstanceApiController
from database_utils.database import Database
from .instance_loader import InstanceLoader, LoadState
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from server.controllers.instance_manager_controller import InstanceManagerController


KSM_DATABASE = "ksm_database"


class InstanceManager(Database, InstanceManagerController):
    __instances: List[ServerInstance]
    __permission_manager: PermissionManager
    __instance_folder: str
    __instance_api: InstanceApiController
    __docker_client: DockerClient

    def __init__(self, instance_api: InstanceApiController, *args, **kwargs):
        self.__instance_api = instance_api
        self.__docker_client = from_env()

        super().__init__(*args, **kwargs)

    def __load_instance(
            self,
            instance_id: int,
            instance_name: str,
            instance_docker_image: str,
            instance_folder: str
    ) -> Optional[ServerInstance]:
        instance_arguments = self.__instance_api.instance_arguments.get_arguments(instance_id)

        port = self.get_port(instance_id)

        instance = ServerInstance(
            self,
            self.__docker_client,
            self.__permission_manager,
            instance_id,
            instance_name,
            instance_docker_image,
            instance_arguments,
            instance_folder,
            port
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

        self._execute(
            "CREATE TABLE IF NOT EXISTS instances ("
            "instance_id INT PRIMARY KEY AUTO_INCREMENT, "
            "name CHAR(128) UNIQUE, "
            "folder_name CHAR(128) UNIQUE, "
            "docker_image CHAR(128)"
            ")"
        )

        self._execute(
            "CREATE TABLE IF NOT EXISTS ports("
            "port INT UNIQUE,"
            "instance_id INT UNIQUE, "
            "FOREIGN KEY (instance_id) REFERENCES instances(instance_id)"
            ")"
        )

    def create_instance(self, name: str, instance_docker_image: str, instance_cmd: str):
        if not (self._connector and self._cursor):
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Database doesn't exist.")
                    .build())

        instance_load = InstanceLoader(self.__instance_folder, name)

        result = instance_load.load()
        if result == LoadState.FOLDER_ALREADY_EXISTS:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Folder is already exists")
                    .build())

        folder_name = "-".join(name.lower().split(" "))

        self._execute(
            "INSERT INTO instances (name, folder_name, docker_image, cmd) VALUES (%s, %s, %s, %s)",
            (name, folder_name, instance_docker_image, instance_cmd)
        )

        self._commit()

        self._execute("SELECT instance_id FROM instances WHERE name = %s", (name, ))
        instance_id = self._cursor.fetchone()[0]
        instance_folder = self.__generate_folder(name)

        self.__load_instance(instance_id, name, instance_docker_image, instance_cmd, instance_folder)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Instance created!").build()

    def __port_exists(self, port: int) -> bool:
        self._execute("SELECT COUNT(*) FROM ports WHERE port = %s",
                      (port,)
                      )

        result = self._fetchone()

        return result[0] > 0

    def __instance_exists_with_port(self, instance_id: int) -> bool:
        self._execute("SELECT COUNT(*) FROM ports WHERE instance_id = %s", (instance_id,))

        result = self._fetchone()
        return result[0] > 0

    def create_port(self, port: int):
        if self.__port_exists(port):
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Port already exists!").build()

        self._execute(
            "INSERT INTO ports (port) "
            "VALUES (%s)",
            (port,)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Port created!").build()

    def delete_port(self, port: int) -> Dict:
        if not self.__port_exists(port):
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Port doesn't exist!").build()

        self._execute(
            "DELETE FROM ports WHERE port = %s",
            (port,)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Port deleted!").build()

    def get_ports(self):
        self._execute("SELECT port, instance_id FROM ports")

        result = self._fetchall()
        out = []
        for port in result:
            out.append({"port": port[0], "instance_id": port[1]})

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("ports", out).build()

    def pin_port_to_instance(self, instance_id: int, port: int) -> Dict:
        if not self.__port_exists(port):
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Port does not exist!").build()

        self._execute(
            "UPDATE ports "
            "SET instance_id = %s "
            "WHERE port = %s",
            (instance_id, port)
        )

        self._commit()

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Port has been pinned to instance!")
                .build())

    def unpin_port_from_instance(self, port: int):
        if not self.__port_exists(port):
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Port does not exist!").build()

        self._execute(
            "UPDATE ports "
            "SET instance_id = NULL "
            "WHERE port = %s",
            (port,)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Port has been unpinned!").build()

    def get_port(self, instance_id: int) -> int:
        if not self.__instance_exists_with_port(instance_id):
            return 0

        self._execute("SELECT port FROM ports WHERE instance_id = %s", (instance_id,))

        result = self._fetchone()

        return result[0]

    def load_folder(self, instance_folder: str):
        self.__instance_folder = instance_folder

    def load_permission_manager(self, permission_manager: PermissionManager):
        self.__permission_manager = permission_manager

    def load_instances(self):
        self._execute("SELECT * FROM instances")
        instances = self._fetchall()

        for instance_data in instances:
            instance_id = instance_data[0]
            instance_name = instance_data[1]
            instance_folder_name = instance_data[2]
            instance_docker_image = instance_data[3]
            instance_folder = self.__generate_folder(instance_folder_name)

            self.__load_instance(
                instance_id,
                instance_name,
                instance_docker_image,
                instance_folder
            )

    @property
    def instances(self) -> List[ServerInstance]:
        return self.__instances
