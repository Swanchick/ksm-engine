from server import InstanceManager
from user import UserManager, SYSTEM_ID
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
        self.__instance_manager.start()
        self.__instance_manager.load_instances()

        self.__user_manager = UserManager()
        self.__user_manager.start()

    def __check_password(self, data) -> bool:
        password = data["password"]

        return self.__engine_settings.check_password(password)

    def instance_call(self, method_name: str, data: Dict):
        if not self.__check_password(data):
            return ResponseBuilder().status(200).message("Forbidden!").build()

        instance_data = data["instance_data"]

        response = self.__instance_manager.request(method_name, instance_data)

        return response

    def instance_create(self, data: Dict):
        pass

    def user_create(self, data: Dict):
        if not self.__check_password(data):
            return ResponseBuilder().status(403).message("Forbidden!").build()

        user_id = data["user_id"]

        if user_id != SYSTEM_ID:
            user = self.__user_manager.get_user_by_id(user_id)

            if not (user and user.is_administrator):
                return ResponseBuilder().status(403).message("Forbidden!").build()

        user_data = data["user_data"]
        name = user_data["name"]
        password = user_data["password"]
        administrator = user_data["administrator"]

        self.__user_manager.create_user(name, password, administrator)

        return ResponseBuilder().status(200).message("User has been created successfully!").build()
