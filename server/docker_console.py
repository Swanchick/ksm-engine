from subprocess import Popen, PIPE
from psutil import Process


class DockerConsole:
    __console: Popen
    __container_id: str
    __folder: str
    __console_pid: int

    def __init__(self, container_id: str, __folder: str):
        self.__container_id = container_id
        self.__folder = __folder

        self.__console = Popen(
            ["docker", "attach", self.__container_id],
            cwd=self.__folder,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE
        )

        self.__console_pid = self.__console.pid

    def send(self, command: str):
        self.__console.stdin.write(f"{command}\n".encode("utf-8"))
        self.__console.stdin.flush()

    def close(self):
        process = Process(self.__console_pid)
        process_children = process.children(recursive=True)

        for child in process_children:
            child.kill()
