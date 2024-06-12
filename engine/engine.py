from server.instance_api import InstanceApi
from server.permission.permissions import Permissions
from user.user_manager import UserManager
from user.user import User
from .settings_engine import EngineSettings
from settings.settings_creator import SettingsCreator
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from typing import Dict, Optional, List
from flask import Flask
from waitress import serve
from cryptography.fernet import Fernet
from json import loads, dumps
from base64 import b64encode, b64decode
from api import Api, ApiCaller, api_data


class Engine(Api):
    __engine_settings: EngineSettings

    __user_manager: UserManager
    __cryptography: Fernet
    __debug: bool

    def __init__(self):
        self.__engine_settings = SettingsCreator().settings("engine")
        self.__debug = self.__engine_settings.debug

        self.__cryptography = Fernet(self.__engine_settings.secret_key)

        self._caller = ApiCaller()
        self._caller.register("instance", api=InstanceApi(self.__engine_settings.instance_folder))

        self.__user_manager = UserManager()
        self._caller.register("user", api=self.__user_manager)

    def encrypt_data(self, data: Dict) -> str:
        if self.__debug:
            return dumps(data)

        json = dumps(data)
        encrypted_json = self.__cryptography.encrypt(json.encode())
        bs64 = b64encode(encrypted_json)

        return bs64.decode()

    def decrypt_data(self, data: Dict) -> Dict:
        if self.__debug:
            return data

        encrypted_data = b64decode(data["data"])
        decrypted_json = self.__cryptography.decrypt(encrypted_data).decode()

        return loads(decrypted_json)

    def __check_engine_password(self, data: Dict) -> bool:
        if "password" not in data:
            return False

        password = data["password"]

        return self.__engine_settings.check_password(password)

    def __get_user_by_key(self, data: Dict) -> Optional[User]:
        if "user_key" not in data:
            return None

        user = self.__user_manager.user_authorization.get_authorized_user(data["user_key"])

        return user

    def start(self, app: Flask):
        try:
            self.__cryptography = Fernet(self.__engine_settings.secret_key)
        except Exception:
            print("Fernet key could not be loaded!")
            print("Setup engine to fix the problem \"python main.py --init\"")

            return

        print("KSM Engine has been successfully started.")

        serve(app, host=self.ip, port=self.port)

    def request(self, routes: List[str], encrypted_data: Dict = None, user: User = None) -> Optional[Dict]:
        if len(routes) == 0:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        data = self.decrypt_data(encrypted_data)

        if not self.__check_engine_password(data):
            return ResponseBuilder().status(HttpStatus.HTTP_FORBIDDEN.value).message("Forbidden!").build()

        api_name = routes[0]

        if "data" in data:
            api_data.save("data", data["data"])

        api = self._caller.get(api_name)
        if api is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        user = self.__get_user_by_key(data)
        api_data.save("user", user)

        response = self._caller.request(routes, api_name=api_name)
        if response is None:
            return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).build()

        return response

    @property
    def user_manager(self) -> UserManager:
        return self.__user_manager

    @property
    def port(self) -> int:
        return self.__engine_settings.port

    @property
    def ip(self) -> str:
        return self.__engine_settings.ip

    @property
    def debug(self) -> bool:
        return self.__debug
