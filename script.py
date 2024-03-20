import time


def test_while():
    a = 0

    while a <= 15:
        print("Sleeping for 1 seconds")
        time.sleep(1)
        a += 1


test_while()
