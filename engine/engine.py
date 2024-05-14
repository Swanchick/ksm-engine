from server.instance_manager import InstanceManager
from permission.permission_manager import PermissionManager
from permission.permissions import Permissions
from user.user_manager import UserManager
from user.user import User
from user.user_authorization import UserAuthorization
from .settings_engine import EngineSettings
from settings.settings_creator import SettingsCreator
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from typing import Dict
from flask import Flask
from waitress import serve
from cryptography.fernet import Fernet
from json import loads, dumps
from base64 import b64encode, b64decode


class Engine:
    __instance_manager: InstanceManager
    __user_manager: UserManager
    __permission_manager: PermissionManager
    __engine_settings: EngineSettings
    __user_authorization: UserAuthorization
    __cryptography: Fernet

    def __init__(self):
        self.__engine_settings = SettingsCreator().settings("engine")

        self.__cryptography = Fernet(self.__engine_settings.secret_key)

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

    def encrypt_data(self, data: Dict) -> str:
        json = dumps(data)
        encrypted_json = self.__cryptography.encrypt(json.encode())
        bs64 = b64encode(encrypted_json)

        return bs64.decode()

    def decrypt_data(self, data: Dict) -> Dict:
        encrypted_data = b64decode(data["data"])
        decrypted_json = self.__cryptography.decrypt(encrypted_data).decode()

        return loads(decrypted_json)

    def __check_engine_password(self, data: Dict) -> bool:
        password = data["password"]

        return self.__engine_settings.check_password(password)

    def __get_user_by_key(self, data: Dict) -> User:
        user = self.__user_authorization.get_authorized_user(data["user_key"])

        return user

    def start(self, app: Flask):
        print("KSM Engine has been successfully started.")
        print(f"Running on http://{self.ip}:{self.port}/")

        serve(app, host=self.ip, port=self.port)

    def instance_call(self, method_name: str, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_data = data["instance_data"]
        instance_data["user_id"] = user.user_id
        response = self.__instance_manager.request(method_name, instance_data)

        return response

    def instance_create(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None or not user.is_administrator:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_data = data["instance_data"]
        instance_data["user_id"] = user.user_id

        response = self.__instance_manager.create_instance(instance_data["name"], instance_data["instance_type"])

        return response

    def get_instance(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)
        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_data = data["instance_data"]
        instance_id = instance_data["instance_id"]
        if not self.__permission_manager.check_permission(user.user_id, instance_id, Permissions.INSTANCE_VIEW):
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_FORBIDDEN.value)
                    .message("Forbidden!")
                    .build())

        instance = self.__instance_manager.get_instance_by_id(instance_data["instance_id"])
        if instance is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Instance not found!").build()

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("instance_data", instance.dict)
                .build())

    def get_instances(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

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

    def get_instance_types(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        instance_packages = SettingsCreator().data()["instance_packages"]

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("instance_types", instance_packages)
                .build())

    def user_create(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

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

    def authorize_user(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

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

    def get_users(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        users = self.__user_manager.get_users()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("users", users).build()

    def get_user(self, encrypted_data: Dict):
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        user = self.__get_user_by_key(data)

        if user is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("User not found!").build()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).addition_data("user", user.dict).build()

    def get_permissions(self, encrypted_data: Dict) -> Dict:
        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        permissions = []

        for permission in Permissions:
            permissions.append({permission.name: permission.value})

        return (ResponseBuilder()
                .status(HttpStatus.HTTP_SUCCESS.value)
                .addition_data("permissions", permissions)
                .build())

    @property
    def port(self) -> int:
        return self.__engine_settings.port

    @property
    def ip(self) -> str:
        return self.__engine_settings.ip

    @property
    def user_manager(self) -> UserManager:
        return self.__user_manager
