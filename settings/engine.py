from .settings import Settings
from .settings_creator import SettingsCreator


@SettingsCreator.register_settings
class EngineSettings(Settings):
    __ip: str
    __port: int
    __name: str
    __instance_folder: str

    settings_name = "engine"

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
