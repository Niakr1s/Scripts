from genericpath import isfile
import os
from pathlib import Path
import sys
import time

def check_yes(answer: str):
    if answer.lower() != "y":
        print("Cancelled")
        sys.exit(0)


cwd = Path(os.getcwd())

files = [file for file in cwd.iterdir() if file.is_file() and file.suffix == ".mp4"]

files_str = "\n".join((str(f) for f in files))
answer = input(f"{len(files)} mp4 files will be zeroed:\n{files_str}\n\nProceed? y/n: ")
check_yes(answer)

while True:
    try:
        for file in files:
            file.write_bytes(b'')

        print("Done")
        break
    except Exception as e:
        print(f"Error occured: {e}, retrying in a while...")
        time.sleep(5)