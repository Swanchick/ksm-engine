from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from .user import User


class AbstractUserManager(ABC):
    @abstractmethod
    def create_user(self, name: str, password: str, administrator: bool):
        pass

    @abstractmethod
    def get_users(self) -> Optional[List[Dict]]:
        pass

    @abstractmethod
    def get_user_by_name(self, name: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass
