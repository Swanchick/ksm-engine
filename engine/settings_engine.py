from settings.abstract_settings import AbstractSettings
from settings.settings_manager import SettingsManager


settings_manager = SettingsManager()


@settings_manager.register_settings
class EngineSettings(AbstractSettings):
    __ip: str
    __port: int
    __name: str
    __instance_folder: str
    __password: str
    __secret_key: str

    settings_name = "engine"

    def set_settings(self, **data):
        self.__ip = data["ip"]
        self.__port = data["port"]
        self.__name = data["name"]
        self.__instance_folder = data["server_instances_folder"]
        self.__password = data["password"]
        self.__secret_key = data["secret_key"]

    def check_password(self, engine_password) -> bool:
        return engine_password == self.__password

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

    @property
    def secret_key(self) -> str:
        return self.__secret_key
