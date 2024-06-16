from database_utils.database import Database
from .user import User
from typing import List, Optional, Dict
from .user_authorization import UserAuthorization
from .user_manager_abstract import AbstractUserManager
from api import Api, CallbackCaller, api_data
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus


class UserManager(Api, AbstractUserManager, Database):
    __user_caller: CallbackCaller
    __user_authorization: UserAuthorization
    _require_user: bool = False

    def __init__(self):
        super().__init__()

        self.__user_authorization = UserAuthorization(self)
        self._caller = CallbackCaller(self, "user")

        self.start()

    def start(self):
        self._execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "user_id INT PRIMARY KEY AUTO_INCREMENT,"
            "name TEXT,"
            "password TEXT,"
            "administrator BOOLEAN DEFAULT false)"
        )

    def request(self, routes: List[str], *args, **kwargs) -> Optional[Dict]:
        if len(routes) != 1:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        response = self._caller.request(routes, api_name="user")

        return response

    @CallbackCaller.register("create_user", api_name="user")
    def create_user(self, name: str, password: str, administrator: bool):
        user = api_data.get("user")
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        if not user.is_administrator:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_FORBIDDEN.value)
                    .message("You cannot create new users!")
                    .build())

        new_user = User(name, password, administrator)

        self._execute(
            "INSERT INTO users (name, password, administrator) VALUES (%s, %s, %s)",
            (new_user.name, new_user.password, new_user.is_administrator)
        )
        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("User has been created!").build()

    @CallbackCaller.register("get_users", api_name="user")
    def get_users(self) -> Optional[List[Dict]]:
        self._execute("SELECT * FROM users")

        users = []

        for user_data in self._cursor.fetchall():
            user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)
            users.append(user.dict)

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("users", users).build()

    @CallbackCaller.register("get", api_name="user")
    def get_user(self):
        user = api_data.get("user")

        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("user", user.dict).build()

    @CallbackCaller.register("authenticate_user", api_name="user")
    def authenticate_user(self) -> Optional[List[Dict]]:
        data = api_data.get("data")
        if not data:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        username = data.get("username")
        password = data.get("password")

        if password is None or username is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        key = self.__user_authorization.authorize_user(username, password)

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("You have authorized successfully!")
                .addition_data("key", key)
                .build())

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        if user_id is None:
            return

        self._execute("SELECT * FROM users WHERE user_id = %s", (user_id,))

        user_data = self._fetchone()
        if not user_data:
            return

        user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)

        return user

    def get_user_by_name(self, name: str) -> Optional[User]:
        if name is None:
            return

        self._execute("SELECT * FROM users WHERE name = %s", (name, ))

        user_data = self._fetchone()
        if not user_data:
            return

        user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)

        return user

    @property
    def user_authorization(self) -> UserAuthorization:
        return self.__user_authorization
