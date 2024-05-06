from abc import ABC, abstractmethod
from typing import Optional, List, Dict


class AbstractUserManager(ABC):
    @abstractmethod
    def create_user(self, name: str, password: str, administrator: bool):
        pass

    @abstractmethod
    def get_users(self) -> Optional[List[Dict]]:
        pass
