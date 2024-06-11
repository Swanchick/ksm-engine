import logging
from typing import List, Dict
from permission.permission_manager import PermissionManager
from permission.permissions import Permissions
from .enums.state import ServerState
from .enums.output import ServerOutput, OutputType
from threading import Thread
from .api.instance_caller import InstanceCaller
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from files.folder_system import FolderSystem
from files.file_system import FileSystem
from docker import DockerClient
from docker.models.containers import Container
from .docker_console import DockerConsole
from .controllers.instance_manager_controller import InstanceManagerController

MAX_OUTPUT_MESSAGES = 100


class ServerInstance(InstanceCaller):
    __docker_client: DockerClient
    __instance_manager: InstanceManagerController

    __instance_id: int
    __name: str
    __folder: str
    __docker_image: str
    __port: int
    __arguments: List[str]

    __container: Container
    __docker_console: DockerConsole
    __output: List[ServerOutput]
    __server_state: ServerState

    __folder_system: FolderSystem
    __file_system: FileSystem

    def __init__(
            self,
            instance_manager: InstanceManagerController,
            docker_client: DockerClient,
            permission_manager: PermissionManager,
            instance_id: int,
            instance_name: str,
            instance_docker_image: str,
            instance_arguments: List[str],
            instance_folder: str,
            port: int
    ):
        super().__init__(self, instance_id, permission_manager)

        self.__instance_manager = instance_manager
        self.__docker_client = docker_client

        self.__instance_id = instance_id
        self.__name = instance_name
        self.__docker_image = instance_docker_image
        self.__arguments = instance_arguments
        self.__folder = instance_folder
        self.__output = []
        self.__server_state = ServerState.STOP
        self.__port = port

        self.__folder_system = FolderSystem(self.__folder)
        self.__file_system = FileSystem(self.__folder)

    def __add_message(self, message: str, output_type: OutputType):
        output = ServerOutput(message, output_type)
        self.__output.append(output)

        if len(self.__output) > MAX_OUTPUT_MESSAGES:
            self.__output.pop(0)

    def __stream_outputs(self):
        for log in self.__container.logs(stream=True):
            message = log.decode('utf-8')

            self.__add_message(message, OutputType.TEXT)

        self.stop()

    @InstanceCaller.register("test", Permissions.INSTANCE_VIEW)
    def test(self):
        print(self.port)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("It works").build()

    @InstanceCaller.register("start", Permissions.INSTANCE_START_STOP)
    def start(self):
        if not self.__arguments:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_NOT_FOUND.value)
                    .message("Arguments not set!")
                    .build())

        if self.__port == 0:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_NOT_FOUND.value)
                    .message("Port not set!")
                    .build())

        if self.__server_state == ServerState.START:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is already started")
                    .build())

        command = ["/bin/bash", "-c", " ".join(self.__arguments)]

        self.__container = self.__docker_client.containers.run(
            image=self.__docker_image,
            name=self.__name,
            command=command,
            volumes={
                self.__folder: {
                    "bind": "/app",
                    "mode": "rw"
                }
            },
            ports={
                f"{self.__port}/tcp": self.__port,
                f"{self.__port}/udp": self.__port
            },
            working_dir="/app",
            remove=True,
            detach=True,
            stdout=True,
            stdin_open=True,
            stderr=True
        )

        self.__server_state = ServerState.START

        self.__docker_console = DockerConsole(self.__container.id, self.__folder)

        stream_output_thread = Thread(target=self.__stream_outputs)
        stream_output_thread.start()

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Server has been successfully started.")
                .build())

    @InstanceCaller.register("send", Permissions.INSTANCE_CONSOLE)
    def send(self, request: str) -> Dict:
        if not self.__docker_console:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is not running")
                    .build())

        self.__docker_console.send(request)

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Message has been sent.")
                .build())

    @InstanceCaller.register("stop", Permissions.INSTANCE_START_STOP)
    def stop(self) -> Dict:
        if self.__server_state == ServerState.STOP:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is not started")
                    .build())

        try:
            self.__container.stop()
        except Exception:
            pass

        self.__docker_console.close()

        self.__server_state = ServerState.STOP
        self.__output = []

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Server has been successfully stopped.")
                .build())

    @InstanceCaller.register("get_output", Permissions.INSTANCE_CONSOLE)
    def get_output(self) -> Dict:
        outputs = []
        for output in self.__output:
            outputs.append(output.message)

        logging.info("Client has received output.")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("instance", {"output": outputs})
                .build())

    @InstanceCaller.register("get_folders", Permissions.FILES_SHOW)
    def get_folders(self, *folders) -> Dict:
        try:
            files = self.__folder_system.open_folder(*folders)
        except Exception:
            raise Exception("There is a problem opening folder!")

        if files is None:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_NOT_FOUND.value)
                    .message("Folder not found!")
                    .build())

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Your folders sir")
                .addition_data("folders", files)
                .build())

    @InstanceCaller.register("create_folder", Permissions.FILES_CREATE)
    def create_folder(self, *folders) -> Dict:
        try:
            self.__folder_system.create_folder(*folders)
        except Exception:
            raise Exception("There is a problem creating folder!")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Folder has been created successfully!")
                .build())

    @InstanceCaller.register("delete_folder", Permissions.FILES_REMOVE)
    def delete_folder(self, *folders) -> Dict:
        try:
            self.__folder_system.delete_folder(*folders)
        except Exception:
            raise Exception("There is a problem deleting folder!")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Folder has been successfully deleted!")
                .build())

    @InstanceCaller.register("open_file", Permissions.FILES_EDIT_VIEW)
    def open_file(self, file_name, *folders) -> Dict:
        try:
            data = self.__file_system.open_file(file_name, *folders)
        except Exception:
            raise Exception("There is a problem opening file!")

        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("File not found!").build()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message(data).build()

    @InstanceCaller.register("create_file", Permissions.FILES_CREATE)
    def create_file(self, file_name, *folders) -> Dict:
        try:
            self.__file_system.create_file(file_name, *folders)
        except Exception:
            raise Exception("There is a problem creating file!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been created!").build()

    @InstanceCaller.register("delete_file", Permissions.FILES_REMOVE)
    def delete_file(self, file_name, *folders) -> Dict:
        try:
            self.__file_system.delete_file(file_name, *folders)
        except Exception:
            raise Exception("There is a problem deleting file!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been deleted!").build()

    @InstanceCaller.register("write_file", Permissions.FILES_EDIT_VIEW)
    def write_file(self, file_name, data, *folders) -> Dict:
        try:
            self.__file_system.write_file(file_name, data, *folders)
        except Exception:
            raise Exception("There is a problem writing file!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been changed!").build()

    @InstanceCaller.register("download_file", Permissions.FILES_DOWNLOAD)
    def download_file(self, file_name, *folders) -> Dict:
        try:
            data = self.__file_system.send_file_bs64(file_name, *folders)
        except Exception:
            raise Exception("There is a problem downloading file!")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("file", {"file_name": file_name, "data": data})
                .build())

    @InstanceCaller.register("receive_file", Permissions.FILES_DOWNLOAD)
    def receive_file(self, file_name, data, *folders) -> Dict:
        try:
            self.__file_system.receive_file_bs64(file_name, data, *folders)
        except Exception:
            raise Exception("There is a problem receiving file!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been received!").build()

    @InstanceCaller.register("get_permissions", Permissions.INSTANCE_PERMISSION_EDIT)
    def get_permission(self) -> Dict:
        try:
            permissions = self._permission_manager.get_all_permissions_from_instance(self.__instance_id)
        except Exception:
            raise Exception("There is a problem getting permissions!")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("users", permissions)
                .build())

    @InstanceCaller.register("add_permission", Permissions.INSTANCE_PERMISSION_EDIT)
    def add_permission(self, user_id: int, permission_type: int) -> Dict:
        try:
            self._permission_manager.add_permission(user_id, self.__instance_id, permission_type)
        except Exception:
            raise Exception("There is a problem adding permission!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Permission has been added!").build()

    @InstanceCaller.register("remove_permission", Permissions.INSTANCE_PERMISSION_EDIT)
    def remove_permission(self, user_id: int, permission_type: int) -> Dict:
        try:
            self._permission_manager.remove_permission(user_id, self.__instance_id, permission_type)
        except Exception:
            raise Exception("There is a problem removing permission!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Permission has been removed!").build()

    @InstanceCaller.register("pin_port", Permissions.INSTANCE_PORT)
    def pin_port(self, port: int) -> Dict:
        result = self.__instance_manager.pin_port_to_instance(self.__instance_id, port)
        if result["status"] != HttpStatus.HTTP_SUCCESS.value:
            return result

        self.__port = port

        return result

    @InstanceCaller.register("unpin_port", Permissions.INSTANCE_PORT)
    def unpin_port(self) -> Dict:
        if self.__port == 0:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_BAD_REQUEST.value)
                    .message("Instance does not have a port!")
                    .build())

        result = self.__instance_manager.unpin_port_from_instance(self.__port)
        if result["status"] != HttpStatus.HTTP_SUCCESS.value:
            return result

        self.__port = 0

        return result

    @property
    def instance_state(self) -> ServerState:
        return self.__server_state

    @property
    def output(self) -> List[ServerOutput]:
        return self.__output

    @property
    def name(self):
        return self.__name

    @property
    def instance_id(self):
        return self.__instance_id
    
    @property
    def dict(self) -> dict:
        return {
            "instance_name": self.__name,
            "instance_id": self.__instance_id,
            "instance_state": self.__server_state.value,
            "port": self.__port

        }

    @property
    def port(self):
        return self.__port
