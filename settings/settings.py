from abc import ABC, abstractmethod


class Settings(ABC):
    settings_name = "base"

    @abstractmethod
    def set_settings(self, **data):
        pass
