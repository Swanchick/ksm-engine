from uuid import uuid4
from utils.hash import HashPassword


class User:
    __user_id: int
    __name: str
    __password: str
    __administrator: bool

    def __init__(self, name: str, password: str, administrator: bool,  user_id: int = None, hash_password: bool = True):
        self.__user_id = user_id if user_id else str(uuid4())
        self.__name = name
        self.__administrator = bool(administrator)

        self.__password = HashPassword.hash_password(password) if hash_password else password

    def check_password(self, password: str) -> bool:
        return HashPassword.check_password(password, self.__password)

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def password(self) -> str:
        return self.__password

    @property
    def is_administrator(self):
        return self.__administrator

    @property
    def dict(self) -> dict:
        return {"user_id": self.__user_id, "name": self.__name, "is_administrator": self.__administrator}
