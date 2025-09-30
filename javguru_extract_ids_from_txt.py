# First, extract filenames in Total Commander (Shift + F12 by default)
# Then run this script, providing that txt file


import re
import sys
from pathlib import Path

if __name__ == "__main__":
    try:
        input_filepath = sys.argv[1]
    except IndexError:
        raise RuntimeError("provide txt file with javguru video list")

    input_filepath = Path(input_filepath)
    input = input_filepath.read_text(encoding="utf8")

    RE = re.compile(r"^\[?(\w+-\d+)\]?", flags=re.MULTILINE)

    for match in RE.finditer(input):
        print(match.group(1))
