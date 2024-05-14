from database_utils.database import Database
from .user import User
from typing import List, Optional, Dict
from .user_manager_abstract import AbstractUserManager

KSM_DATABASE = "ksm_database"


class UserManager(AbstractUserManager, Database):
    def start(self):
        self._connect(KSM_DATABASE)
        self._cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY AUTO_INCREMENT,"
                             "name TEXT,"
                             "password text,"
                             "administrator BOOLEAN DEFAULT false)")

    def create_user(self, name: str, password: str, administrator: bool):
        self._connect(KSM_DATABASE)

        user = User(name, password, administrator)

        self._cursor.execute("INSERT INTO users (name, password, administrator) VALUES (%s, %s, %s)",
                             (user.name, user.password, user.is_administrator))
        self._connector.commit()

        return user

    def get_users(self) -> Optional[List[Dict]]:
        self._connect(KSM_DATABASE)

        self._cursor.execute("SELECT * FROM users")

        users = []

        for user_data in self._cursor.fetchall():
            user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)
            users.append(user.dict)

        return users

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        if user_id is None:
            return

        self._connect(KSM_DATABASE)

        self._cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

        user_data = self._cursor.fetchone()
        if not user_data:
            return

        user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)

        return user

    def get_user_by_name(self, name: str) -> Optional[User]:
        if name is None:
            return

        self._connect(KSM_DATABASE)

        self._cursor.execute("SELECT * FROM users WHERE name = %s", (name, ))

        user_data = self._cursor.fetchone()
        if not user_data:
            return

        user = User(user_data[1], user_data[2], user_data[3], user_data[0], False)

        return user
