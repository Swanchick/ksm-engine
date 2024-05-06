from utils import JsonReader
from .settings import Settings
from typing import Dict
from .settings_manager import SettingsManager


class SettingsCreator:
    __path: str
    __settings: Settings

    def __init__(self, path: str = "settings.json"):
        self.__path = path

    def __read_file(self):
        reader = JsonReader(self.__path)

        return reader.read()

    def settings(self, settings_type: str):
        settings_manager = SettingsManager()

        self.__settings = settings_manager.get_settings(settings_type)()

        data = self.__read_file()
        if settings_type not in data:
            return {}

        data = data[settings_type]

        self.__settings.set_settings(**data)

        return self.__settings

    def data(self) -> Dict:
        return self.__read_file()

    def save(self, data: Dict):
        reader = JsonReader(self.__path)
        reader.write(data)
