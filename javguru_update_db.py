# WARNING

import argparse
from pathlib import Path

from javguru.db import JavguruDatabase
from javguru.files import extract_id_and_description


def main():
    parser = argparse.ArgumentParser(description="Javguru Database Manager")
    parser.add_argument(
        "--db",
        help="Database file path (default: database.db)",
        required=True,
    )
    parser.add_argument(
        "--mp4s",
        help="A text files with a list of mp4 files, each line in format of '[ID] Some description.mp4'. Such list for example can be obtained from Total Commander command Shift+F12.",
        required=True,
    )
    args = parser.parse_args()

    db = JavguruDatabase(args.db)

    mp4s = Path(args.mp4s).read_text(encoding="utf8").strip().splitlines()
    inserted = 0
    for i, mp4 in enumerate(mp4s):
        prefix = f"[{i:05}]"
        try:
            id, description = extract_id_and_description(mp4)
        except Exception as e:
            print(
                f"{prefix} Error: couldn't extract id and description for {mp4}, reason: {e}"
            )
            continue

        try:
            db.insert_row(id=id, description=description)
        except Exception as e:
            print(f"{prefix} {id} Error: couldn't insert row, reason: {e}")
            continue

        inserted += 1
        print(f"{prefix} {id} inserted")

    print(f"Done, inserted {inserted} of {len(mp4s)}")


if __name__ == "__main__":
    main()
