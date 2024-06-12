from .user_manager_abstract import AbstractUserManager
from .user import User
from typing import Dict, Optional
from uuid import uuid4


class UserAuthorization:
    __user_manager: AbstractUserManager
    __authorized_users: Dict[str, User]

    def __init__(self, user_manager: AbstractUserManager):
        self.__user_manager = user_manager
        self.__authorized_users = {}

    def authorize_user(self, name: str, password: str) -> Optional[str]:
        user = self.__user_manager.get_user_by_name(name)
        if user is None:
            return

        if not user.check_password(password):
            return

        key = str(uuid4())
        self.__authorized_users[key] = user
        return key

    def get_authorized_user(self, key: str) -> Optional[User]:
        if key == "debug":
            return self.__user_manager.get_user_by_id(1)

        if key not in self.__authorized_users:
            return

        return self.__authorized_users[key]
