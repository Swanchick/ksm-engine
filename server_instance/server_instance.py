from subprocess import Popen, PIPE
from user import Permission
from typing import List
from .server_state import ServerState
from threading import Thread
from utils import Callbacks


class ServerInstance(Callbacks):
    __name: str
    __program_name: str
    __arguments: List[str]

    __process: Popen
    __permission: Permission = Permission()
    __output: List[str]
    __server_state: ServerState
    __server_thread: Thread

    __server_on_output_get: callable(str)

    def __init__(self, name: str, program_name: str, arguments: List[str]):
        self.__name = name
        self.__program_name = program_name
        self.__arguments = arguments
        self.__output = []
        self.__server_process = True
        self.__server_state = ServerState.STOPPED

        super().__init__()

    def __start_thread(self):
        if not self.__process:
            return

        while True:
            output = self.__process.stdout.readline().decode("utf-8")

            if output != "":
                self.__output.append(output)

            if not self.__server_process:
                break

        self.__process.terminate()

    def start(self):
        command = [self.__program_name] + self.__arguments

        self.__process = Popen(command, stdout=PIPE, stdin=PIPE)
        self.__server_state = ServerState.STARTED

        self.__server_thread = Thread(target=self.__start_thread)
        self.__server_thread.start()

        print(f"Server Instance: {self.__name} has been started.")

    def stop(self):
        if not (self.__process and self.__server_thread):
            return

        self.__server_process = False

        print(f"Server Instance: {self.__name} has been stopped.")

    @property
    def server_state(self) -> ServerState:
        return self.__server_state

    @property
    def output(self) -> List[str]:
        return self.__output
