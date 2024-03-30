from user import UserManager, PermissionManager
from server import InstanceManager


instance_manager = InstanceManager()
instance_manager.start()
instance_manager.create_instance("test_web2")

