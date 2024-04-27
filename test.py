import permission
from permission import PermissionManager, Permissions


permission_manager = PermissionManager()
permission_manager.start()

print(permission_manager.get_all_permissions_from_instance(6))

