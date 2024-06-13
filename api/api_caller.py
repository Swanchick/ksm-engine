from .base_caller import BaseCaller
from .base_api import BaseApi
from typing import Dict, List, Optional
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus


class ApiCaller(BaseCaller):
    __api: Dict[str, BaseApi]

    def __init__(self):
        self.__api = {}

    def get(self, name: str) -> Optional[BaseApi]:
        if name not in self.__api:
            return

        return self.__api[name]

    def register(self, name: str, api: BaseApi = None, *args, **kwargs):
        if name in self.__api:
            return

        self.__api[name] = api

    def request(self, routes: List[str], *args, **kwargs) -> Optional[Dict]:
        if len(routes) <= 1:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        name = routes[0]
        if name not in self.__api:
            return ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        api = self.__api[name]

        response = api.request(routes[1:], *args, **kwargs)

        return response
