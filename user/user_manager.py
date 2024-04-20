from database_utils import Database
from .user import User
from typing import List, Optional, Dict


class UserManager(Database):
    def start(self):
        self._connector = self._connect("ksm_database")
        self._cursor = self._connector.cursor()

        self._cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY AUTO_INCREMENT,"
                             "name TEXT,"
                             "password text,"
                             "administrator BOOLEAN DEFAULT false)")

    def create_user(self, name: str, password: str, administrator: bool):
        if not (self._connector and self._cursor):
            return

        user = User(name, password, administrator)

        self._cursor.execute("INSERT INTO users (name, password, administrator) VALUES (%s, %s, %s)",
                             (user.name, user.password, user.is_administrator))
        self._connector.commit()

        return user

    def get_users(self) -> Optional[List[Dict]]:
        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * FROM users")

        users = []

        for user_data in self._cursor.fetchall():
            user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)
            users.append(user.dict)

        return users

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        if user_id is None:
            return

        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

        user_data = self._cursor.fetchone()
        if not user_data:
            return

        user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)

        return user

    def get_user_by_name(self, name: str) -> Optional[User]:
        if name is None:
            return

        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * FROM users WHERE name = %s", (name, ))

        user_data = self._cursor.fetchone()
        if not user_data:
            return

        print(user_data)

        user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)

        return user
