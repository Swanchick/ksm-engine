from typing import Dict


class ResponseBuilder:
    __response: Dict

    def __init__(self):
        self.__response = {"status": None}

    def message(self, message: str):
        self.__response["message"] = message

        return self

    def status(self, status: int):
        self.__response["status"] = status

        return self

    def addition_data(self, key: str, addition_data: Dict):
        if key in self.__response:
            return self

        self.__response[key] = addition_data

        return self

    def build(self) -> Dict:
        return self.__response
