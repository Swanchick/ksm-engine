import logging
from subprocess import Popen, PIPE
from typing import List, Optional, Dict
from permission.permission_manager import PermissionManager
from permission.permissions import Permissions
from .enums.state import ServerState
from .enums.output import ServerOutput, OutputType
from threading import Thread
from settings.settings_creator import SettingsCreator
from .api.instance_caller import InstanceCaller
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from files.folder_system import FolderSystem
from files.file_system import FileSystem
from psutil import Process

SETTING_FILE = "ksm_settings.json"
MAX_OUTPUT_MESSAGES = 100


class ServerInstance(InstanceCaller):
    __instance_id: int
    __name: str
    __folder: str
    __cmd: str
    __docker_image: str
    __arguments: List[str]

    __process: Optional[Popen]
    __output: List[ServerOutput]
    __server_state: ServerState

    __folder_system: FolderSystem
    __file_system: FileSystem

    def __init__(self, permission_manager: PermissionManager, instance_id: int, name: str, instance_folder: str):
        super().__init__(self, instance_id, permission_manager)

        self.__id = instance_id
        self.__name = name
        self.__folder = instance_folder
        self.__output = []
        self.__server_state = ServerState.STOP

        self.__folder_system = FolderSystem(self.__folder)
        self.__file_system = FileSystem(self.__folder)

    def __monitor_server(self):
        if not self.__process:
            return

        while True:
            if self.__process.returncode is not None:
                break
        
        self.__server_state = ServerState.STOP
        self.__process = None

    def __add_message(self, message: str, output_type: OutputType):
        output = ServerOutput(message, output_type)
        self.__output.append(output)

        if len(self.__output) > MAX_OUTPUT_MESSAGES:
            self.__output.pop(0)

    def __get_output(self):
        if not self.__process:
            return

        while self.__server_state == ServerState.START:
            message = self.__process.stdout.readline().decode("utf-8")

            if message == "":
                continue

            self.__add_message(message, OutputType.TEXT)

    def __get_err(self):
        if not self.__process:
            return

        while self.__server_state == ServerState.START:
            message = self.__process.stderr.readline().decode("utf-8")

            if message == "":
                return

            self.__add_message(message, OutputType.ERR)

    @InstanceCaller.register("test", Permissions.INSTANCE_VIEW)
    def test(self):
        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("It works").build()

    @InstanceCaller.register("server_start", Permissions.INSTANCE_START_STOP)
    def start(self):
        if self.__server_state == ServerState.START:
            logging.error("Server already started")

            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is already started")
                    .build())

        command = [self.__cmd] + self.__arguments
        try:
            self.__process = Popen(command, cwd=self.__folder, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        except Exception:
            raise Exception("There is a problem running instance!")

        self.__server_state = ServerState.START

        thread_monitor_server = Thread(target=self.__monitor_server)
        thread_get_output = Thread(target=self.__get_output)
        thread_get_err = Thread(target=self.__get_err)

        thread_monitor_server.start()
        thread_get_output.start()
        thread_get_err.start()

        logging.info(f"Server Instance: {self.__name} has been started with pid {self.__process.pid}.")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Server has been successfully started.")
                .build())

    @InstanceCaller.register("server_send", Permissions.INSTANCE_CONSOLE)
    def send(self, request: str) -> Dict:
        try:
            self.__process.stdin.write(f"{request}\n".encode("utf-8"))
            self.__process.stdin.flush()
        except Exception:
            raise Exception("Cannot send command to process!")

        logging.info(f"Client has sent command \"{request}\" to process.")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Message has been sent.")
                .build())

    @InstanceCaller.register("server_stop", Permissions.INSTANCE_START_STOP)
    def stop(self) -> Dict:
        if not self.__process:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is not started")
                    .build())

        try:
            process = Process(self.__process.pid)
            children_precesses = process.children(recursive=True)

            for child in children_precesses:
                child.terminate()

            process.terminate()

            logging.info(f"Server Instance: {self.__name} has been stopped.")
        except Exception as e:
            raise Exception("Cannot stop instance! Probably it is not running!")

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

    @InstanceCaller.register("get_permissions", Permissions.INSTANCE_PERMISSION_EDIT)
    def get_permission(self) -> Dict:
        try:
            permissions = self._permission_manager.get_all_permissions_from_instance(self.__id)
        except Exception:
            raise Exception("There is a problem getting permissions!")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("users", permissions)
                .build())

    @InstanceCaller.register("add_permission", Permissions.INSTANCE_PERMISSION_EDIT)
    def add_permission(self, user_id: int, permission_type: int) -> Dict:
        try:
            self._permission_manager.add_permission(user_id, self.__id, permission_type)
        except Exception:
            raise Exception("There is a problem adding permission!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Permission has been added!").build()

    @InstanceCaller.register("remove_permission", Permissions.INSTANCE_PERMISSION_EDIT)
    def remove_permission(self, user_id: int, permission_type: int) -> Dict:
        try:
            self._permission_manager.remove_permission(user_id, self.__id, permission_type)
        except Exception:
            raise Exception("There is a problem removing permission!")

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Permission has been removed!").build()

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
        return self.__id

    @property
    def dict(self) -> dict:
        return {"instance_name": self.__name, "instance_id": self.__instance_id, "instance_state": self.__server_state.value}
