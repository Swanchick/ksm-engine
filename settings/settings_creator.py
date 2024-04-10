from utils import JsonReader
from .settings import Settings
from typing import Dict, Type


class SettingsCreator:
    __path: str
    __settings: Settings

    settings_types: Dict[str, Type[Settings]] = {}

    def __init__(self, path: str = "settings.json"):
        self.__path = path

    def __read_file(self):
        reader = JsonReader(self.__path)

        return reader.read()

    @classmethod
    def register_settings(cls, settings_cls: Type[Settings]):
        name = settings_cls.settings_name
        cls.settings_types[name] = settings_cls

        return settings_cls

    def settings(self, settings_type: str):
        self.__settings = self.settings_types[settings_type]()

        data = self.__read_file()
        if settings_type not in data:
            return {}

        data = data[settings_type]

        self.__settings.set_settings(**data)

        return self.__settings

    def data(self) -> Dict:
        return self.__read_file()
