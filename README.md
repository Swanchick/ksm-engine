# Kyryl's Server Manager (KSM)

## Introduction

1. Our app, Kyryl's Server Manager (KSM), makes it super easy to handle different types of servers, like Python, PHP, and even gaming servers like Minecraft or Garry's Mod.
2. To start using the program, first clone the "ksm-engine" and "ksm-panel" repositories from the Git repository, set up a MySQL database, then configure the database information in the "settings.json" file located in the "ksm-engine" folder, and also set up details about the "ksm-engine" in the "settings.json" file in the "ksm-panel" folder.
3. Using KSM is easy! When you open it, you'll see a list of your servers. From there, you can make new ones, change settings on existing ones, and even make multiple servers run at the same time. Plus, you can decide who gets to do what with each server, so you're always in control. Whether you're new to servers or a pro, KSM makes managing them a breeze.

## Body/Analysis

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
2. **Builder Pattern**: The `ResponseBuilder` class is used to implement a builder pattern to build responses in http server.
3. **Singleton Pattern**: The `SettingsManager` class is implemented as a singleton to ensure there is only one instance of it in the application.

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
