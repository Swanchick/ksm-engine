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
