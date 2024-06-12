from abc import abstractmethod
from .base_api import BaseApi
from typing import List


class BaseCaller(BaseApi):
    @abstractmethod
    def get(self, name: str):
        pass

    @abstractmethod
    def register(self, name: str, *args, **kwargs):
        pass

    @abstractmethod
    def request(self, routes: List[str], api_name: str = None, *args, **kwargs):
        pass
