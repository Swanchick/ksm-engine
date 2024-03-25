from uuid import uuid4


class User:
    __user_id: str
    __name: str
    __password: str

    def __init__(self, name: str, password: str, user_id: str = None):
        self.__user_id = user_id if user_id else str(uuid4())
        self.__name = name
        self.__password = password
