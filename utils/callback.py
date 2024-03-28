from typing import List
from abc import ABC


class Callback:
    __name: str
    _callback: callable

    def __init__(self, name: str, callback: callable):
        self.__name = name
        self._callback = callback

    def call(self, *args, **kwargs):
        return self._callback(*args, **kwargs)

    @property
    def name(self):
        return self.__name


class Callbacks(ABC):
    """
    Basically, it should be an interface but, python doesn't have interfaces, so I use abstract class instead :)
    """
    _callbacks: List[Callback]

    def __init__(self):
        self._callbacks = []

        super().__init__()

    def register_callback(self, name: str, callback: callable):
        callback = Callback(name, callback)
        self._callbacks.append(callback)

    def call(self, name, *args, **kwargs):
        for callback in self._callbacks:
            if callback.name == name:
                return callback.call(*args, **kwargs)