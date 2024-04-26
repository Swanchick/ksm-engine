class SavedPermission:
    __user_id: int
    __instance_id: int
    __permission: int
    __is_administrator: bool
    
    def __init__(self, user_id: int, instance_id: int, permission: int = 0, is_administrator: bool = True):
        self.__user_id = user_id
        self.__instance_id = instance_id
        self.__permission = permission
        self.__is_administrator = is_administrator
    
    @property
    def user_id(self) -> int:
        return self.__user_id
    
    @property
    def instance_id(self) -> int:
        return self.__instance_id

    @property
    def permission(self) -> int:
        return self.__permission

    @property
    def is_administrator(self) -> bool:
        return self.__is_administrator
