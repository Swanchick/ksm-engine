from user import UserManager, PermissionManager

permission_manager = PermissionManager()
permission_manager.start()

# permission_manager.add_permission(1, 1, "permission_console", True)
# permission_manager.add_permission(1, 2, "permission_start_stop", True)

print(permission_manager.check_permission(1, 2, "permission_start_stop"))
