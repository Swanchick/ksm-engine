from server.instance_arguments import InstanceArguments


instance_arguments = InstanceArguments()
instance_arguments.start()

args = instance_arguments.get_arguments(1)
for arg in args:
    print(arg[0])
