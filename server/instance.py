from subprocess import Popen, PIPE
from typing import List, Optional
from .state import ServerState
from utils import Callbacks
from .output import ServerOutput, OutputType
from threading import Thread
from utils import SettingsBuilder, InstanceSettings


class ServerInstance(Callbacks):
    __id: int
    __name: str
    __folder: str
    __settings: InstanceSettings

    __process: Optional[Popen]
    __output: List[ServerOutput]
    __server_state: ServerState

    def __init__(self, instance_id: int, name: str, instance_folder: str):
        self.__id = instance_id
        self.__name = name
        self.__folder = instance_folder
        self.__output = []
        self.__server_process = True
        self.__server_state = ServerState.STOP

        super().__init__()

    def __monitor_server(self):
        if not self.__process:
            return

        self.call("on_server_start")

        while True:
            print(f"{self.__name}: {self.__process.returncode}")

            if self.__process.returncode is not None:
                break
        
        self.__server_state = ServerState.STOP
        self.__process = None

        self.call("on_server_stop")

    def __add_message(self, message: str, output_type: OutputType):
        output = ServerOutput(message, output_type)
        self.__output.append(output)

        self.call("on_output_get", output)

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
        self.__settings = (SettingsBuilder(f"{self.__folder}settings.json")
                           .get_settings("instance")
                           .get())

    def start(self):
        if self.__server_state == ServerState.START:
            return

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

    def send(self, request: str):
        if not (self.__process and self.__server_state == ServerState.START):
            return

        self.__process.stdin.write(f"{request}\n".encode("utf-8"))
        self.__process.stdin.flush()

        self.call("on_request_send", request)

    def stop(self):
        if not self.__process:
            return

        self.__process.terminate()

    @property
    def server_state(self) -> ServerState:
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