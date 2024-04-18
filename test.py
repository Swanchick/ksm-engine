from user import PermissionManager, Permissions


permission_manager = PermissionManager()
permission_manager.start()
permission_manager.remove_permission(4, 1, Permissions.INSTANCE_USER_EDIT)
