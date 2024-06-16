from typing import List, Optional, Dict
from docker import DockerClient, from_env
from .permission.permission_manager import PermissionManager
from .permission.permissions import Permissions
from .instance import ServerInstance
from .controllers.instance_api_controller import InstanceApiController
from database_utils.database import Database
from .instance_loader import InstanceLoader, LoadState
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from server.controllers.instance_manager_controller import InstanceManagerController
from api import Api, CallbackCaller, api_data
from user.user import User


class InstanceManager(Api, Database, InstanceManagerController):
    __instances: List[ServerInstance]
    __permission_manager: PermissionManager
    __instance_folder: str
    __instance_api: InstanceApiController
    __docker_client: DockerClient

    def __init__(self, instance_folder: str, permission_manager: PermissionManager, instance_api: InstanceApiController, *args, **kwargs):
        self.__instances = []

        self.__instance_folder = instance_folder
        self.__permission_manager = permission_manager
        self.__instance_api = instance_api
        self.__docker_client = from_env()

        self._caller = CallbackCaller(self, "instance_manager")

        super().__init__(*args, **kwargs)

        self.start()

    def __load_instance(
            self,
            instance_id: int,
            instance_name: str,
            instance_docker_image: str,
            instance_folder: str
    ) -> Optional[ServerInstance]:
        instance_arguments = self.__instance_api.instance_arguments

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

    def __get_instance_by_id(self, instance_id: int) -> Optional[ServerInstance]:
        for instance in self.__instances:
            if instance.instance_id == instance_id:
                return instance

    def request(self, routes: List[str], *args, **kwargs) -> Optional[Dict]:
        user = api_data.get("user")
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        response = self._caller.request(routes, api_name="instance_manager")

        return response

    def start(self):
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

    @CallbackCaller.register("create", api_name="instance_manager")
    def create_instance(self):
        data = api_data.get("data")
        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        name = data.get("name")
        instance_docker_image = data.get("docker_image")

        if name is None or instance_docker_image is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        instance_load = InstanceLoader(self.__instance_folder, name)

        result = instance_load.load()
        if result == LoadState.FOLDER_ALREADY_EXISTS:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Folder is already exists")
                    .build())

        folder_name = "-".join(name.lower().split(" "))

        self._execute(
            "INSERT INTO instances (name, folder_name, docker_image) VALUES (%s, %s, %s)",
            (name, folder_name, instance_docker_image)
        )

        self._commit()

        self._execute("SELECT instance_id FROM instances WHERE name = %s", (name, ))
        instance_id = self._fetchone()[0]
        instance_folder = self.__generate_folder(name)

        self.__load_instance(instance_id, name, "", instance_folder)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Instance created!").build()

    def __port_exists(self, port: int) -> bool:
        self._execute(
            "SELECT COUNT(*) FROM ports WHERE port = %s",
            (port,)
        )

        result = self._fetchone()

        return result[0] > 0

    def __instance_exists_with_port(self, instance_id: int) -> bool:
        self._execute("SELECT COUNT(*) FROM ports WHERE instance_id = %s", (instance_id,))

        result = self._fetchone()
        return result[0] > 0

    @CallbackCaller.register("get", api_name="instance_manager")
    def get_instances(self) -> Dict:
        instances = []

        user: User = api_data.get("user")
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").buid()

        for instance in self.__instances:
            instance_id = instance.instance_id

            if not self.__permission_manager.check_permission(user, instance_id, Permissions.INSTANCE_VIEW):
                continue

            instances.append(instance.dict)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("instances", instances).build()

    @CallbackCaller.register("create_port", api_name="instance_manager")
    def create_port(self):
        data = api_data.get("data")
        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        port = data.get("port")
        if port is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        if self.__port_exists(port):
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Port already exists!").build()

        self._execute(
            "INSERT INTO ports (port) "
            "VALUES (%s)",
            (port,)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Port created!").build()

    @CallbackCaller.register("delete_port", api_name="instance_manager")
    def delete_port(self) -> Dict:
        data = api_data.get("data")
        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        port = data.get("port")
        if port is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        if not self.__port_exists(port):
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Port doesn't exist!").build()

        self._execute(
            "DELETE FROM ports WHERE port = %s",
            (port,)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Port deleted!").build()

    @CallbackCaller.register("get_ports", api_name="instance_manager")
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

    @CallbackCaller.register("get_permissions", api_name="instance_manager")
    def get_permissions(self) -> Dict:
        permissions = []

        for permission in Permissions:
            permissions.append({permission.name: permission.value})

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("permissions", permissions).build()

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
