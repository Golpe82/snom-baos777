import time
import sys


def wait(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(f"{remaining} seconds remaining...")
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\n0 seconds remaining\n")
