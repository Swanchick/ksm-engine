from typing import Optional, Tuple
from settings.settings_creator import SettingsCreator
from mysql.connector import connect as mysql_connect
from abc import ABC, abstractmethod
from .settings_database import DatabaseSettings

KSM_DATABASE = "ksm_database"


class Database(ABC):
    __settings: DatabaseSettings
    _connector = None
    _cursor = None

    def __init__(self):
        self.__settings = (SettingsCreator()
                           .settings("database"))

        self.__init_database()
        super().__init__()

    def __init_database(self):
        self._connect()

        self._cursor.execute("CREATE DATABASE IF NOT EXISTS ksm_database")
        self._connector.commit()
        self._cursor.close()

        self._connector.disconnect()

    def _connect(self, database_name: Optional[str] = None):
        connect = mysql_connect(
            host=self.__settings.ip,
            user=self.__settings.user,
            password=self.__settings.password,
            database=database_name
        )

        self._connector = connect
        self._cursor = connect.cursor()

    def _execute(self, query: str, args: Tuple = ()):
        self._connect(KSM_DATABASE)

        self._cursor.execute(query, args)

    def _commit(self):
        self._connector.commit()

    def _fetchone(self) -> Tuple:
        return self._cursor.fetchone()

    def _fetchall(self):
        return self._cursor.fetchall()

    @abstractmethod
    def start(self):
        ...
