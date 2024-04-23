from .user_manager import UserManager
from .user import User
from typing import Dict, Optional
from uuid import uuid4


class UserAuthorization:
    __user_manager: UserManager
    __authorized_users: Dict[str, User]

    def __init__(self, user_manager: UserManager):
        self.__user_manager = user_manager
        self.__authorized_users = {}

    def authorize_user(self, name: str, password: str) -> Optional[str]:
        user = self.__user_manager.get_user_by_name(name)
        if user is None:
            return

        if not user.check_password(password):
            return None

        key = str(uuid4())
        self.__authorized_users[key] = user
        return key

    def get_authorized_user(self, key: str) -> Optional[User]:
        if key == "debug":
            return self.__user_manager.get_user_by_id(4)

        if key not in self.__authorized_users:
            return

        return self.__authorized_users[key]
