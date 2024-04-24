from server import InstanceManager
from permission import PermissionManager, Permissions
from user import UserManager, UserAuthorization, User
from .settings_engine import EngineSettings
from settings import SettingsCreator
from utils import ResponseBuilder, HttpStatus
from typing import Dict


class Engine:
    __instance_manager: InstanceManager
    __user_manager: UserManager
    __permission_manager: PermissionManager
    __engine_settings: EngineSettings
    __user_authorization: UserAuthorization

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

        self.__user_authorization = UserAuthorization(self.__user_manager)

    def __check_engine_password(self, data: Dict) -> bool:
        password = data["password"]

        return self.__engine_settings.check_password(password)

    def __get_user_by_key(self, data: Dict) -> User:
        user = self.__user_authorization.get_authorized_user(data["user_key"])

        return user

    def instance_call(self, method_name: str, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_data = data["instance_data"]
        instance_data["user_id"] = user.user_id
        response = self.__instance_manager.request(method_name, instance_data)

        return response

    def instance_create(self, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None or not user.is_administrator:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_data = data["instance_data"]
        instance_data["user_id"] = user.user_id

        self.__instance_manager.create_instance(instance_data["name"], instance_data["instance_type"])

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("Instance has been successfully created!")
                .build())

    def get_instance(self, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_data = data["instance_data"]
        instance = self.__instance_manager.get_instance_by_id(instance_data["instance_id"])
        if instance is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Instance not found!").build()

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("instance_data", instance.dict)
                .build())

    def get_instances(self, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instances = self.__instance_manager.instances
        instances_out = []

        user_id = user.user_id

        for instance in instances:
            instance_id = instance.instance_id

            if not (self.__permission_manager.check_permission(user_id, instance_id, Permissions.INSTANCE_VIEW)
                    or user.is_administrator):
                continue

            instances_out.append(instance.dict)

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("instances", instances_out)
                .build())

    def user_create(self, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if not user.is_administrator:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user_data = data["user_data"]
        name = user_data["name"]
        password = user_data["password"]
        administrator = user_data["administrator"]

        self.__user_manager.create_user(name, password, administrator)

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("User has been created successfully!")
                .build())

    def authorize_user(self, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user_data = data["user_data"]

        key = self.__user_authorization.authorize_user(user_data["name"], user_data["password"])
        if not key:
            return ResponseBuilder().status(HttpStatus.HTTP_UNAUTHORIZED.value).message("User not found!").build()

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .message("User has been authorized!")
                .addition_data("user_data", {"key": key})
                .build())

    def get_users(self, data: Dict) -> Dict:
        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        users = self.__user_manager.get_users()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("users", users).build()

    @property
    def port(self) -> int:
        return self.__engine_settings.port

    @property
    def ip(self) -> str:
        return self.__engine_settings.ip
