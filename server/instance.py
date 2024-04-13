from subprocess import Popen, PIPE
from typing import List, Optional
from user import PermissionManager, PERMISSION_START_STOP
from .state import ServerState
from .output import ServerOutput, OutputType
from threading import Thread
from .settings_instance import InstanceSettings
from settings import SettingsCreator
from api import ApiCaller
from utils import ResponseBuilder

SETTING_FILE = "ksm_settings.json"


class ServerInstance(ApiCaller):
    __id: int
    __name: str
    __folder: str
    __settings: InstanceSettings

    __process: Optional[Popen]
    __output: List[ServerOutput]
    __server_state: ServerState
    __permission_manager: PermissionManager

    def __init__(self, permission_manager: PermissionManager, instance_id: int, name: str, instance_folder: str):
        super().__init__()

        self.__permission_manager = permission_manager
        self.__id = instance_id
        self.__name = name
        self.__folder = instance_folder
        self.__output = []
        self.__server_process = True
        self.__server_state = ServerState.STOP

        self.__init_api()

    def __init_api(self):
        self.register("server_start", self.start)
        self.register("server_stop", self.stop)
        self.register("get_last_output", self.get_last_output)

    def __monitor_server(self):
        if not self.__process:
            return

        while True:
            if self.__process.returncode is not None:
                break
        
        self.__server_state = ServerState.STOP
        self.__process = None

    def get_last_output(self):
        data = {
            "output": self.__output[-1].message if self.__output else None
        }

        return ResponseBuilder().status(200).addition_data("instance", data).build()

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

    def _start_process(self):
        pass

    def start(self, user_id):
        if not self.__permission_manager.check_permission(user_id, self.__id, PERMISSION_START_STOP):
            return ResponseBuilder().status(500).message("Server is already started").build()

        if self.__server_state == ServerState.START:
            return ResponseBuilder().status(500).message("Server is already started").build()

        self.__setup()

        command = [self.__settings.program, f"{self.__folder}{self.__settings.script}"] + self.__settings.arguments
        self.__process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        self.__server_state = ServerState.START

        thread_monitor_server = Thread(target=self.__monitor_server)
        thread_get_output = Thread(target=self.__get_output)
        thread_get_err = Thread(target=self.__get_err)

        thread_monitor_server.start()
        thread_get_output.start()
        thread_get_err.start()

        print(f"Server Instance: {self.__name} has been started.")

        return ResponseBuilder().status(200).message("Server has been successfully started.").build()

    def send(self, request: str):
        if not (self.__process and self.__server_state == ServerState.START):
            return ResponseBuilder().status(500).message("Server is not started").build()

        self.__process.stdin.write(f"{request}\n".encode("utf-8"))
        self.__process.stdin.flush()

    def stop(self):
        if not self.__process:
            return ResponseBuilder().status(500).message("Server is not started").build()

        self.__process.terminate()

        print(f"Server Instance: {self.__name} has been stopped.")

        return ResponseBuilder().status(200).message("Server has been successfully stopped.").build()

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
