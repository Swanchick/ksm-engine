from abc import ABC, abstractmethod
from typing import List


class Settings(ABC):
    settings_name = "base"

    @abstractmethod
    def set_settings(self, **data):
        pass
