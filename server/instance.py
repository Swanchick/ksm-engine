from subprocess import Popen, PIPE
from typing import List, Optional, Dict
from permission import PermissionManager, Permissions
from .state import ServerState
from .output import ServerOutput, OutputType
from threading import Thread
from .settings_instance import InstanceSettings
from settings import SettingsCreator
from api import InstanceCaller
from utils import ResponseBuilder, HttpStatus
from files import FolderSystem, FileSystem
from psutil import Process

SETTING_FILE = "ksm_settings.json"


class ServerInstance(InstanceCaller):
    __id: int
    __name: str
    __folder: str
    __settings: InstanceSettings

    __process: Optional[Popen]
    __output: List[ServerOutput]
    __server_state: ServerState

    __folder_system: FolderSystem
    __file_system: FileSystem

    def __init__(self, permission_manager: PermissionManager, instance_id: int, name: str, instance_folder: str):
        super().__init__(permission_manager)

        self.__id = instance_id
        self.__name = name
        self.__folder = instance_folder
        self.__output = []
        self.__server_process = True
        self.__server_state = ServerState.STOP

        self.__folder_system = FolderSystem(self.__folder)
        self.__file_system = FileSystem(self.__folder)

        self.__init_api()

    def __init_api(self):
        self._register("server_start", self.start, self.__id, Permissions.INSTANCE_START_STOP)
        self._register("server_stop", self.stop, self.__id, Permissions.INSTANCE_START_STOP)
        self._register("get_last_output", self.get_last_output, self.__id, Permissions.INSTANCE_CONSOLE)
        self._register("get_folders", self.get_folders, self.__id, Permissions.FILES_SHOW)
        self._register("create_folder", self.create_folder, self.__id, Permissions.FILES_CREATE)
        self._register("delete_folder", self.delete_folder, self.__id, Permissions.FILES_REMOVE)
        self._register("open_file", self.open_file, self.__id, Permissions.FILES_EDIT_VIEW)
        self._register("create_file", self.create_file, self.__id, Permissions.FILES_CREATE)
        self._register("delete_file", self.delete_file, self.__id, Permissions.FILES_REMOVE)
        self._register("write_file", self.write_file, self.__id, Permissions.FILES_EDIT_VIEW)

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

        # To Do:
        # Send this information to client

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

    def __setup(self):
        self.__settings = (SettingsCreator(f"{self.__folder}{SETTING_FILE}")
                           .settings("instance"))

    def start(self):
        if self.__server_state == ServerState.START:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is already started")
                    .build())

        self.__setup()

        command = [self.__settings.program] + self.__settings.arguments
        self.__process = Popen(command, cwd=self.__folder, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        print(self.__process.pid)
        self.__server_state = ServerState.START

        thread_monitor_server = Thread(target=self.__monitor_server)
        thread_get_output = Thread(target=self.__get_output)
        thread_get_err = Thread(target=self.__get_err)

        thread_monitor_server.start()
        thread_get_output.start()
        thread_get_err.start()

        print(f"Server Instance: {self.__name} has been started.")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Server has been successfully started.")
                .build())

    def send(self, request: str):
        self.__process.stdin.write(f"{request}\n".encode("utf-8"))
        self.__process.stdin.flush()

    def stop(self):
        if not self.__process:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value)
                    .message("Server is not started")
                    .build())

        process = Process(self.__process.pid)
        children_precesses = process.children(recursive=True)

        for child in children_precesses:
            child.terminate()

        process.terminate()

        self.__server_state = ServerState.STOP

        print(f"Server Instance: {self.__name} has been stopped.")

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Server has been successfully stopped.")
                .build())

    def get_last_output(self):
        data = {
            "output": self.__output[-1].message if self.__output else None
        }

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("instance", data).build()

    def get_folders(self, *folders) -> Dict:
        files = self.__folder_system.open_folder(*folders)

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

    def create_folder(self, *folders) -> Dict:
        self.__folder_system.create_folder(*folders)

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Folder has been created successfully!")
                .build())

    def delete_folder(self, *folders) -> Dict:
        self.__folder_system.delete_folder(*folders)

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Folder has been successfully deleted!")
                .build())

    def open_file(self, file_name, *folders) -> Dict:
        data = self.__file_system.open_file(file_name, *folders)
        if data is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("File not found!").build()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message(data).build()

    def create_file(self, file_name, *folders) -> Dict:
        self.__file_system.create_file(file_name, *folders)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been created!").build()

    def delete_file(self, file_name, *folders) -> Dict:
        self.__file_system.delete_file(file_name, *folders)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been deleted!").build()

    def write_file(self, file_name, data, *folders) -> Dict:
        self.__file_system.write_file(file_name, data, *folders)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("File has been changed!").build()

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
        return {"instance_name": self.__name, "instance_id": self.__id, "instance_state": self.__server_state.value}
