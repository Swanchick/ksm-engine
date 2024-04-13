from server import InstanceManager
from user import UserManager
from .settings_engine import EngineSettings
from settings import SettingsCreator
from utils import ResponseBuilder
from typing import Dict



class Engine:
    __instance_manager: InstanceManager
    __user_manager: UserManager
    __engine_settings: EngineSettings

    def __init__(self):
        self.__engine_settings = SettingsCreator().settings("engine")

        self.__instance_manager = InstanceManager()
        self.__instance_manager.load_folder(self.__engine_settings.instance_folder)
        self.__instance_manager.load_instances()
        self.__user_manager = UserManager()

    def instance_call(self, data: Dict, method_name: str):
        password = data["password"]

        if not self.__engine_settings.check_password(password):
            return ResponseBuilder().status(403).message("Forbidden!").build()

        instance_data = data["instance_data"]

        self.__instance_manager.request(method_name, instance_data)

    def instance_create(self, data):
        pass
