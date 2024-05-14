from typing import Optional
from settings.settings_creator import SettingsCreator
from mysql.connector import connect as mysql_connect
from abc import ABC, abstractmethod
from .settings_database import DatabaseSettings


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

    @abstractmethod
    def start(self):
        ...
