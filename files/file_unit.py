from .file_type import FileType


class FileUnit:
    __file_name: str
    __file_type: FileType

    def __init__(self, file_name: str, file_type: FileType):
        self.__file_name = file_name
        self.__file_type = file_type

    def __repr__(self):
        return str(self.dict)

    @property
    def file_name(self) -> str:
        return self.__file_name

    @property
    def file_type(self) -> FileType:
        return self.__file_type

    @property
    def dict(self) -> dict:
        return {"file_name": self.__file_name, "file_type": self.__file_type.value}
