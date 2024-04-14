from server import InstanceManager
from user import SYSTEM_ID, UserManager, PermissionManager
from .settings_engine import EngineSettings
from settings import SettingsCreator
from utils import ResponseBuilder
from typing import Dict


class Engine:
    __instance_manager: InstanceManager
    __user_manager: UserManager
    __permission_manager: PermissionManager
    __engine_settings: EngineSettings

    def __init__(self):
        self.__engine_settings = SettingsCreator().settings("engine")

        self.__instance_manager = InstanceManager()
        self.__instance_manager.load_folder(self.__engine_settings.instance_folder)
        self.__instance_manager.start()

        self.__user_manager = UserManager()
        self.__user_manager.start()

        self.__permission_manager = PermissionManager()
        self.__permission_manager.start()
        self.__permission_manager.load_user_manager(self.__user_manager)

        self.__instance_manager.load_permission_manager(self.__permission_manager)
        self.__instance_manager.load_instances()

    def __check_password(self, data: Dict) -> bool:
        password = data["password"]

        return self.__engine_settings.check_password(password)

    def __check_administrator(self, data: Dict) -> bool:
        user_id = data["user_id"] if "user_id" in data else None

        user = self.__user_manager.get_user_by_id(user_id)

        return user_id == SYSTEM_ID or user and user.is_administrator

    def instance_call(self, method_name: str, data: Dict) -> Dict:
        if not self.__check_password(data):
            return ResponseBuilder().status(200).message("Forbidden!").build()

        instance_data = data["instance_data"]

        response = self.__instance_manager.request(method_name, instance_data)

        return response

    def instance_create(self, data: Dict) -> Dict:
        if not self.__check_password(data):
            return ResponseBuilder().status(403).message("Forbidden!").build()

        instance_data = data["instance_data"]
        if not self.__check_administrator(instance_data):
            return ResponseBuilder().status(403).message("Forbidden!").build()

        self.__instance_manager.create_instance(instance_data["name"], instance_data["instance_type"])

        return ResponseBuilder().status(200).message("Instance has been successfully created!").build()

    def user_create(self, data: Dict) -> Dict:
        if not self.__check_password(data):
            return ResponseBuilder().status(403).message("Forbidden!").build()

        if not self.__check_administrator(data):
            return ResponseBuilder().status(403).message("Forbidden!").build()

        user_data = data["user_data"]
        name = user_data["name"]
        password = user_data["password"]
        administrator = user_data["administrator"]

        self.__user_manager.create_user(name, password, administrator)

        return ResponseBuilder().status(200).message("User has been created successfully!").build()
