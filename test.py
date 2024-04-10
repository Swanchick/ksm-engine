class Power:
    registered_classes = {}

    def __call__(self, the_class):
        self.registered_classes[the_class.name] = the_class

        print(self.registered_classes)

        return the_class


@Power()
class Test:
    name: str = "Test"


@Power()
class Test2:
    name: str = "Test2"
