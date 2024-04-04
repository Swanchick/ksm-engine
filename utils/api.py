from abc import ABC, abstractmethod
from .callback import Callback
from typing import List, Optional, Dict


class Api(ABC):
    @abstractmethod
    def request(self, method_name: str, data: Dict) -> Optional[Dict]:
        pass


class ApiCaller(ABC):
    _callbacks: List[Callback]

    def __init__(self):
        self._callbacks = []

        super().__init__()

    def __is_callback_exists(self, name: str) -> bool:
        for callback in self._callbacks:
            if callback.name == name:
                return True

        return False

    def register(self, name: str, callback: callable):
        callback = Callback(name, callback)
        self._callbacks.append(callback)

    def unregister(self, name: str):
        for callback in self._callbacks:
            if callback.name == name:
                self._callbacks.remove(callback)
                break

    def unregister_all(self):
        self._callbacks = []

    def call(self, name, *args, **kwargs):
        for callback in self._callbacks:
            if callback.name == name:
                return callback.call(*args, **kwargs)
