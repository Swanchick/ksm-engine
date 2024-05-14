from settings.abstract_settings import AbstractSettings
from settings.settings_manager import SettingsManager


settings_manager = SettingsManager()


@settings_manager.register_settings
class DatabaseSettings(AbstractSettings):
    __ip: str
    __user: str
    __port: int
    __password: str

    settings_name = "database"

    def set_settings(self, **data):
        self.__ip = data["ip"]
        self.__user = data["user"]
        self.__port = data["port"]
        self.__password = data["password"]

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def user(self) -> str:
        return self.__user

    @property
    def port(self):
        return self.__port

    @property
    def password(self):
        return self.__password
