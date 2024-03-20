import time
import threading
import subprocess

run_while = True


def test_while(process):
    outputs = 0

    while True:
        if process.poll() is not None:
            break

        output = process.stdout

        if output is None:
            continue

        read_output = output.readline()
        print(f"{outputs}: {read_output.decode("utf-8")}", end="")

        outputs += 1


if __name__ == "__main__":
    process = subprocess.Popen(["python", "script.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(0.5)

    thread1 = threading.Thread(target=test_while, args=(process,))
    thread1.start()
