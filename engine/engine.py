from server import InstanceManager
from user import UserManager
from .settings_engine import EngineSettings
from settings import SettingsCreator
from typing import Dict


class Engine:
    __instance_manager: InstanceManager
    __user_manager: UserManager
    __engine_settings: EngineSettings

    def __init__(self):
        self.__instance_manager = InstanceManager()
        self.__instance_manager.load_instances()
        self.__user_manager = UserManager()

        self.__engine_settings = SettingsCreator().settings("engine")

    def instance_call(self, data: Dict, method_name: str):
        password = data["password"]

        if not self.__engine_settings.check_password(password):
            return {"status": 403, "message": "Forbidden"}

        instance_data = data["instance_data"]

        self.__instance_manager.request(method_name, instance_data)

    def instance_create(self, data):
        pass
