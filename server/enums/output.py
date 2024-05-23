from enum import Enum


class OutputType(Enum):
    """Enumeration of possible output types"""
    TEXT = 1
    ERR = 2


class ServerOutput:
    __message: str
    __output_type: OutputType

    def __init__(self, message, output_type):
        self.__message = message
        self.__output_type = output_type

    @property
    def message(self):
        return self.__message

    @property
    def output_type(self):
        return self.__output_type
