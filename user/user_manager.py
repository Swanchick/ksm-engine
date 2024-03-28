from utils import Database
from .user import User
from typing import List, Optional


class UserManager(Database):
    def start(self):
        self._connector = self._connect("ksm_database")
        self._cursor = self._connector.cursor()

        self._cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY AUTO_INCREMENT, name TEXT, "
                             "password text)")

    def get_users_by_id(self, uuid: str):
        pass

    def create_user(self, name, password):
        if not (self._connector and self._cursor):
            return

        user = User(name, password)

        self._cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (user.name, user.password))
        self._connector.commit()

        return user

    def get_users(self) -> Optional[List[User]]:
        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * FROM users")

        users = []

        for user_data in self._cursor.fetchall():
            users.append(User(user_data[1], user_data[2], user_data[0], False))

        return users
