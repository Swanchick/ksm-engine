from typing import Optional
from .settings import SettingsBuilder, DatabaseSettings
from mysql.connector import connect as mysql_connect
from abc import ABC, abstractmethod


class Database(ABC):
    __settings: DatabaseSettings
    _connector = None
    _cursor = None

    def __init__(self):
        self.__settings = (SettingsBuilder()
                           .settings("database")
                           .get())

        self.__init_database()
        super().__init__()

    def __init_database(self):
        connect = self._connect()

        cursor = connect.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS ksm_database")
        connect.commit()
        cursor.close()

        connect.disconnect()

    def _connect(self, database_name: Optional[str] = None):
        connect = mysql_connect(
            host=self.__settings.ip,
            user=self.__settings.user,
            password=self.__settings.password,
            database=database_name
        )

        return connect

    @abstractmethod
    def start(self):
        ...
