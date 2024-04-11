from settings.settings import Settings
from typing import List
from settings.settings_manager import SettingsManager


settings_manager = SettingsManager()


@settings_manager.register_settings
class InstanceSettings(Settings):
    __program: str
    __script: str
    __arguments: List[str]

    settings_name = "instance"

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
