from settings import Settings
from typing import List
from settings import SettingsManager


settings_manager = SettingsManager()


@settings_manager.register_settings
class InstanceSettings(Settings):
    __program: str
    __arguments: List[str]

    settings_name = "instance"

    def set_settings(self, **data):
        self.__program = data["program"]
        self.__arguments = data["arguments"]

    @property
    def program(self) -> str:
        return self.__program

    @property
    def arguments(self) -> List[str]:
        return self.__arguments
