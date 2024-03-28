from subprocess import Popen, PIPE
from user import Permission
from typing import List, Optional
from .state import ServerState
from utils import Callbacks
from .output import ServerOutput, OutputType
from threading import Thread


class ServerInstance(Callbacks):
    __name: str
    __program_name: str
    __arguments: List[str]

    __process: Optional[Popen]
    __permission: Permission = Permission()
    __output: List[ServerOutput]
    __server_state: ServerState

    def __init__(self, name: str, program_name: str, arguments: List[str]):
        self.__name = name
        self.__program_name = program_name
        self.__arguments = arguments
        self.__output = []
        self.__server_process = True
        self.__server_state = ServerState.STOPPED

        super().__init__()

    def __monitor_server(self):
        self.call("on_server_start")

        if not self.__process:
            return

        while True:
            if self.__process.returncode is not None:
                self.__server_process = ServerState.STOPPED
                break

        self.__process.kill()
        self.__server_state = ServerState.STOPPED
        self.__process = None

        self.call("on_server_stop")

    def __add_message(self, message: str, output_type: OutputType):
        output = ServerOutput(message, output_type)
        self.__output.append(output)

        self.call("on_server_get", output)

    def __get_output(self):
        if not self.__process:
            return

        while self.__server_state == ServerState.STARTED:
            message = self.__process.stdout.readline().decode("utf-8")

            if message == "":
                continue

            self.__add_message(message, OutputType.TEXT)

    def __get_err(self):
        if not self.__process:
            return

        while self.__server_state == ServerState.STARTED:
            message = self.__process.stderr.readline().decode("utf-8")

            if message == "":
                return

            self.__add_message(message, OutputType.ERR)

    def start(self):
        command = [self.__program_name] + self.__arguments

        self.__process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        self.__server_state = ServerState.STARTED

        thread_monitor_server = Thread(target=self.__monitor_server)
        thread_get_output = Thread(target=self.__get_output)
        thread_get_err = Thread(target=self.__get_err)

        thread_monitor_server.start()
        thread_get_output.start()
        thread_get_err.start()

        print(f"Server Instance: {self.__name} has been started.")

    def send(self, request: str):
        if not (self.__process and self.__server_state == ServerState.STARTED):
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