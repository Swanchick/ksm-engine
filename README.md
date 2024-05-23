# KSM Engine
## KSM Preview [https://youtu.be/flDqwnqLZ7g]

### Made by `Kyryl Lebedenko` from `EKfu-23`!

---
## Introduction:

1. Our app, Kyryl's Server Manager (KSM), makes it super easy to handle different types of servers, like Python, PHP, and even gaming servers like Minecraft or Garry's Mod.
2. To start using the program, first clone the "ksm-engine" and "ksm-panel" repositories from the Git repository, set up a MySQL database, then configure the database information in the "settings.json" file located in the "ksm-engine" folder, and also set up details about the "ksm-engine" in the "settings.json" file in the "ksm-panel" folder.
3. Using KSM is easy! When you open it, you'll see a list of your servers. From there, you can make new ones, change settings on existing ones, and even make multiple servers run at the same time. Plus, you can decide who gets to do what with each server, so you're always in control. Whether you're new to servers or a pro, KSM makes managing them a breeze.

## Body/Analysis:

Let's analyze how the program covers the functional requirements, including the implementation of OOP principles (Encapsulation, Inheritance, Polymorphism, Abstraction), as well as the SOLID principles and design patterns.

### OOP Pillars:

1. **Encapsulation**: Encapsulation is demonstrated throughout the code by using classes to encapsulate related functionality and data. For example, classes like `ServerInstance`, `UserManager`, `PermissionManager`, etc., encapsulate their respective functionalities and data attributes.
2. **Inheritance**: Inheritance is utilized in the code to create relationships between classes. For instance, the `UserManager` and `PermissionManager` classes inherit from the `Database` class, and the `Settings` class serves as a base class for other specific settings classes.
3. **Polymorphism**: Polymorphism is demonstrated through method overriding and method overloading. Subclasses override methods from their parent classes to provide specific implementations. For example, the `start()` method is overridden in various classes like `UserManager`, `PermissionManager`, etc., to provide specific functionality.
4. **Abstraction**: Abstraction is used to hide the internal implementation details of classes and expose only relevant functionalities. For instance, the `Settings` class provides an abstract method `set_settings()`, leaving the implementation details to its subclasses.

### SOLID Principles:
1. **Single Responsibility Principle (SRP)**: Each class has a single responsibility, such as `ServerInstance` for managing server instances, `UserManager` for managing users, and `PermissionManager` for managing permissions.
2. **Open/Closed Principle (OCP)**: The code is open for extension but closed for modification. New functionalities can be added through subclasses or new classes without altering the existing codebase significantly.
3. **Liskov Substitution Principle (LSP)**: Subclasses are used interchangeably with their parent classes where needed. For example, `ServerInstance` instances are treated uniformly within the `InstanceManager` class.
4. **Interface Segregation Principle (ISP)**: Interfaces are segregated into specific responsibilities. For instance, the `AbstractUserManager` interface defines methods related to user management.
5. **Dependency Inversion Principle (DIP)**: High-level modules (e.g., `InstanceManager`, `UserManager`) depend on abstractions (interfaces) rather than concrete implementations.

### Design Patterns:
1. **Factory Method**: The `SettingsCreator` class acts as a factory method to create specific settings objects based on the provided settings type.

```py
class SettingsCreator:
    __path: str
    __settings: Settings

    def __init__(self, path: str = "settings.json"):
        self.__path = path

    def __read_file(self):
        reader = JsonReader(self.__path)

        return reader.read()

    def settings(self, settings_type: str):
        settings_manager = SettingsManager()

        self.__settings = settings_manager.get_settings(settings_type)()

        data = self.__read_file()
        if settings_type not in data:
            return {}

        data = data[settings_type]

        self.__settings.set_settings(**data)

        return self.__settings

    def data(self) -> Dict:
        return self.__read_file()

    def save(self, data: Dict):
        reader = JsonReader(self.__path)
        reader.write(data)
```

2. **Builder Pattern**: The `ResponseBuilder` class is used to implement a builder pattern to build responses in http server.

```py
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
```
### Example of ResponseBuilder
```py
print((ResponseBuilder()
       .status(200)
       .message("Hello World")
       .addition_data("some_data", {"data1": "Another hello world"})
       .build())
      )
```

Output:
```json
{
   "status": 200,
   "message": "Hello World",
   "some_data": {
      "data1": "Another hello world"
   }
}
```


3. **Singleton Pattern**: The `SettingsManager` class is implemented as a singleton to ensure there is only one instance of it in the application.

```py
class SettingsManager:
    __settings_types: Dict[str, Type[Settings]] = {}

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)

        return cls.instance

    def register_settings(self, cls: Type[Settings]):
        name = cls.settings_name

        self.__settings_types[name] = cls

        return cls

    def get_settings(self, name) -> Type[Settings]:
        return self.__settings_types[name]
```

### Reading from File & Writing to File:
The program reads settings from a JSON file using the `JsonReader` class and writes data to the same file using the `write()` method of the `JsonReader` class. This functionality is encapsulated within the `SettingsCreator` class.

### Database Usage:
The program interacts with a database (assumed to be MySQL based on the table creation SQL statements) using the `Database` class. Classes like `UserManager` and `PermissionManager` utilize database operations to manage users, permissions, and instances.

## Results and Summary

### Results Functional Requirement:
1. **User Management**:
   - Implemented user management functionalities include creating users, retrieving users by ID or name, and user authorization.
2. **Instance Management**:
   - Implemented instance management functionalities include creating, starting, stopping instances, and managing instance permissions.
3. **Settings Management**:
   - Implemented settings management functionalities include registering and retrieving settings for different components of the application.
4. **Database Management**
   - Implemented database management functionalities include connecting to the database and initializing it.
5. **API and Callbacks**:
   - Implemented an API for instance-related operations and callback mechanisms for executing instance methods.
6. **File System Operations**:
   - Implemented file system operations such as creating, deleting folders and files, reading, and writing to files.
7. **Permission Management**:
   - Implemented permission management functionalities for controlling access to various features based on user roles.

### Conclusions Functional Requirement:

The application successfully implements core functionalities related to user, instance, settings, database, and permission management, providing a comprehensive system for managing resources and permissions within the application.
The modular design of the application allows for easy extension and integration of new features or components in the future. Each component is encapsulated, making it easier to modify or extend without affecting other parts of the system.
The permission management system ensures that access to sensitive operations or data is restricted based on user roles, enhancing the security of the application.
By implementing features such as error handling and status reporting, the application aims to be reliable and resilient to failures.

### Extensibility Possibilities:

1. **Additional Functionality**: Introduce new functionalities such as logging, monitoring, or task scheduling to enhance the application's capabilities.
2. **Integration with External Services**: Extend the application to integrate with external services or APIs for additional functionality or data sources.
3. **Integration of Docker**: In the future, we plan to incorporate Docker container support into KSM. This will allow us to manipulate performance and isolate processes more effectively. Ultimately, both the ksm-engine and ksm-panel will transition into Docker containers, simplifying their setup process significantly.
4. **Enhanced User Interface**: Develop a user-friendly interface or dashboard to interact with the application, providing users with better visibility and control over system operations.
5. **Optimization and Performance**: Probably after course work, I'll rewrite ksm-engine to other programming language, such as, `Rust` or `C#`, to make backend part as fast as possible.
