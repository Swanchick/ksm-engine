from abc import ABC, abstractmethod
from typing import List
from .callback import Callback


class Caller(ABC):
    registered_callbacks: List[Callback] = []

    _class_instance: type

    def __init__(self, class_instance):
        self._callbacks = []
        self._class_instance = class_instance

        super().__init__()

    def register(self, name: str, *args):
        pass

    @abstractmethod
    def call(self, name: str, *args, **kwargs):
        pass
