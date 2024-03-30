from .json_reader import JsonReader
from abc import ABC, abstractmethod
from typing import List


class Settings(ABC):
    @abstractmethod
    def set_settings(self, **data):
        pass


class DatabaseSettings(Settings):
    __ip: str
    __user: str
    __port: int
    __password: str

    def set_settings(self, **data):
        self.__ip = data["ip"]
        self.__user = data["user"]
        self.__port = data["port"]
        self.__password = data["password"]

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def user(self) -> str:
        return self.__user

    @property
    def port(self):
        return self.__port

    @property
    def password(self):
        return self.__password


class EngineSettings(Settings):
    __ip: str
    __port: int
    __name: str
    __instance_folder: str

    def set_settings(self, **data):
        self.__ip = data["ip"]
        self.__port = data["port"]
        self.__name = data["name"]
        self.__instance_folder = data["server_instances_folder"]

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def port(self) -> int:
        return self.__port

    @property
    def name(self) -> str:
        return self.__name

    @property
    def instance_folder(self) -> str:
        return self.__instance_folder


class InstanceSettings(Settings):
    __program: str
    __script: str
    __arguments: List[str]

    def set_settings(self, **data):
        self.__program = data["program"]
        self.__script = data["script"]
        self.__arguments = data["arguments"]

    @property
    def program(self) -> str:
        return self.__program

    @property
    def script(self):
        return self.__script

    @property
    def arguments(self) -> List[str]:
        return self.__arguments


_settings_types = {
    "database": DatabaseSettings,
    "engine": EngineSettings,
    "instance": InstanceSettings
}


class SettingsBuilder:
    __path: str
    __settings: Settings

    def __init__(self, path: str = "settings.json"):
        self.__path = path

    def __read_file(self, settings_type: str):
        reader = JsonReader(self.__path)

        return reader.read(settings_type)

    def get_settings(self, settings_type: str):
        self.__settings = _settings_types[settings_type]()

        data = self.__read_file(settings_type)
        self.__settings.set_settings(**data)

        return self

    def get(self):
        return self.__settings
