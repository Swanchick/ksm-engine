import time
import threading
import subprocess

run_while = True
command_outputs = []


def test_while(process: subprocess.Popen):
    global command_outputs

    outputs = 0

    while True:
        if process.poll() is not None:
            break

        output = process.stdout

        if output is None:
            continue

        read_output = output.readline()

        out = f"{outputs}: {read_output.decode("utf-8")}"
        command_outputs.append(out)

        outputs += 1

        if not run_while:
            break

    process.terminate()


def commands():
    while True:
        command = input("Enter command: ")

        if command == "get":
            print(command_outputs[-1])
        elif command == "exit":
            break


if __name__ == "__main__":
    process = subprocess.Popen(["python", "script.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(0.5)

    thread1 = threading.Thread(target=test_while, args=(process,))
    thread1.start()
    thread2 = threading.Thread(target=commands)
    thread2.start()