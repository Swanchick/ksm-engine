from settings.abstract_settings import AbstractSettings
from settings.settings_manager import SettingsManager
from typing import List


settings_manager = SettingsManager()


@settings_manager.register_settings
class InstanceSettings(AbstractSettings):
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
