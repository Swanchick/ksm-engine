from .yaml_reader import YamlReader
from abc import ABC, abstractmethod


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


_settings_types = {
    "database": DatabaseSettings
}


class SettingsBuilder:
    __path: str
    __settings: Settings

    def __init__(self, path: str = "settings.yaml"):
        self.__path = path

    def __read_file(self, settings_type: str):
        reader = YamlReader(self.__path)

        return reader.read(settings_type)

    def get_settings(self, settings_type: str):
        self.__settings = _settings_types[settings_type]()

        data = self.__read_file(settings_type)
        self.__settings.set_settings(**data)

        return self

    def get(self):
        return self.__settings
