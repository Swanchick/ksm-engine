class Permission:
    __name: str
    __start_server: bool
    __stop_server: bool

    def __init__(self, name: str = "User", start_server: bool = False, stop_server: bool = False):
        self.__name = name
        self.__start_server = start_server
        self.__stop_server = stop_server
