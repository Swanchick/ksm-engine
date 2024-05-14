from abc import ABC, abstractmethod


class AbstractSettings(ABC):
    settings_name = "base"

    @abstractmethod
    def set_settings(self, **data):
        pass
