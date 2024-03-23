a = True

while a:
    print("Enter command: ")

    command = input()

    if command.isdigit():
        for i in range(int(command)):
            print(f"{i}: Hello World")

    elif command == "exit":
        a = False
        print("Exit bye bye!")
    else:
        print("Invalid command")
