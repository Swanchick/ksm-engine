from typing import Dict, Type, Optional


class ApiData:
    __data: Dict[str, Type]

    def __init__(self):
        self.__data = {}

    def save(self, name: str, data: Optional[Type]):
        self.__data[name] = data

    def get(self, name: str):
        if name not in self.__data:
            return

        return self.__data[name]


api_data: ApiData = ApiData()
