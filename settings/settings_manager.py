from .settings import Settings
from typing import Dict, Type


class SettingsManager:
    __settings_types: Dict[str, Type[Settings]] = {}

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)

        return cls.instance

    def register_settings(self, cls: Type[Settings]):
        name = cls.settings_name

        self.__settings_types[name] = cls

        return cls

    def get_settings(self, name) -> Type[Settings]:
        return self.__settings_types[name]