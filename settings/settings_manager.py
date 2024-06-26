from .abstract_settings import AbstractSettings
from typing import Dict, Type


class SettingsManager:
    __settings_types: Dict[str, Type[AbstractSettings]] = {}

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)

        return cls.instance

    def register_settings(self, cls: Type[AbstractSettings]):
        name = cls.settings_name

        self.__settings_types[name] = cls

        return cls

    def get_settings(self, name) -> Type[AbstractSettings]:
        return self.__settings_types[name]