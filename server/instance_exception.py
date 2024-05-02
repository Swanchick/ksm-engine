class InstanceException(Exception):
    __message: str

    def __init__(self, message: str):
        self.__message = message
        super().__init__()

    def __str__(self):
        return self.__message
