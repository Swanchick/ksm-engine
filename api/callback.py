from .base_api import BaseApi


class Callback(BaseApi):
    _name: str
    _callback: callable

    def __init__(self, name: str, callback: callable):
        self._name = name
        self._callback = callback

    def request(self, *args, **kwargs):
        return self._callback(*args, **kwargs)

    @property
    def name(self):
        return self._name
