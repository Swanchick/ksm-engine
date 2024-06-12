from api.base_caller import BaseCaller
from api.api import Api
from typing import List, Dict, Optional
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from user.user import User


class EngineCaller(BaseCaller):
    registered_api: Dict[str, Api]

    def __init__(self):
        super().__init__(None)

        self.registered_api = {}

    def register(self, name: str, api: Api):
        if name in self.registered_api:
            return

        self.registered_api[name] = api

    def call(self, user: User, name: str, routes: List[str], data: Dict) -> Dict:
        if name not in self.registered_api:
            return (ResponseBuilder()
                    .status(HttpStatus.HTTP_NOT_FOUND.value)
                    .message("Not found!")
                    .build())

        api = self.registered_api[name]
        response = api.request(routes[1:], data, user=user)

        return response

    def get(self, name) -> Optional[Api]:
        if name not in self.registered_api:
            return

        return self.registered_api[name]
