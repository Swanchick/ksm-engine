from .base_caller import BaseCaller
from typing import Dict, Optional, List
from .callback import Callback
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from typing import Type
from .api import Api


class CallbackCaller(BaseCaller):
    registered_callbacks: Dict[str, List[Callback]] = {}
    __apis: Dict = {}

    def __init__(self, api: Type[Api], api_name: str):
        self.__apis[api_name] = api

    def get(self, name: str, api_name: str = None) -> Optional[Callback]:
        if api_name is None:
            return

        callbacks = self.registered_callbacks[api_name]

        for callback in callbacks:
            if callback.name == name:
                return callback

        return

    @classmethod
    def register(cls, name: str, api_name: str = None, *args, **kwargs) -> callable:
        if api_name not in cls.registered_callbacks:
            cls.registered_callbacks[api_name] = []

        def decorator(func: callable):
            callback = Callback(name, func)
            cls.registered_callbacks[api_name].append(callback)

            return func

        return decorator

    def request(self, routes: List[str], api_name: str = None, *args, **kwargs) -> Optional[Dict]:
        if len(routes) != 1:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        name = routes[0]

        if api_name not in self.registered_callbacks:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        if api_name not in self.__apis:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        api = self.__apis[api_name]
        callback = self.get(name, api_name=api_name)
        if callback is None:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        try:
            response = callback.request(api, *args, **kwargs)
        except Exception as e:
            return ResponseBuilder().status(HttpStatus.HTTP_INTERNAL_SERVER_ERROR.value).message(str(e)).build()
        else:
            return response
