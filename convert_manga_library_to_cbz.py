import argparse
import zipfile
from pathlib import Path

from send2trash import send2trash


def convert_to_cbz(manga_root_path, delete_original=False):
    """
    Convert manga chapters to CBZ format

    Args:
        manga_root_path: Path to main manga folder
        delete_original: If True, deletes original image folders after conversion
    """
    manga_path = Path(manga_root_path)

    if not manga_path.exists():
        print(f"Error: Path '{manga_path}' does not exist!")
        return

    # Find all chapter subfolders
    for item in manga_path.iterdir():
        if item.is_dir():
            # Check if it's a chapter folder (you might want to adjust this logic)
            print(f"Processing chapter: {item.name}")

            # Create CBZ file path
            cbz_path = item.parent / f"{item.name}.cbz"

            # Get all image files (common manga formats)
            image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
            image_files = []

            for ext in image_extensions:
                image_files.extend(item.glob(f"*{ext}"))

            # Sort files naturally (for proper page order)
            def natural_sort_key(s):
                import re

                return [
                    int(text) if text.isdigit() else text.lower()
                    for text in re.split(r"(\d+)", s.name)
                ]

            image_files = sorted(image_files, key=natural_sort_key)

            if not image_files:
                print(f"  No image files found in {item.name}")
                continue

            # Create CBZ file
            with zipfile.ZipFile(cbz_path, "w", zipfile.ZIP_DEFLATED) as cbz_file:
                for img_file in image_files:
                    # Preserve folder structure inside CBZ if needed
                    arcname = img_file.name
                    cbz_file.write(img_file, arcname)
                    print(f"  Added: {img_file.name}")

            print(f"  Created: {cbz_path.name}")

            # Delete original folder if requested
            if delete_original:
                send2trash(item)
                print(f"  Deleted original folder: {item.name}")


def batch_convert_all_manga(manga_library_path, delete_original=False):
    """
    Convert all manga in your library
    """
    library_path = Path(manga_library_path)

    for manga_folder in library_path.iterdir():
        if manga_folder.is_dir():
            print(f"\n{'=' * 50}")
            print(f"Processing manga: {manga_folder.name}")
            print(f"{'=' * 50}")
            convert_to_cbz(manga_folder, delete_original=delete_original)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert manga chapters to CBZ format")
    parser.add_argument("path", help="Path to manga folder or library")
    parser.add_argument(
        "--batch", action="store_true", help="Process entire manga library"
    )
    parser.add_argument(
        "--delete", action="store_true", help="Delete original folders after conversion"
    )

    args = parser.parse_args()

    if args.batch:
        batch_convert_all_manga(args.path, delete_original=args.delete)
    else:
        convert_to_cbz(args.path, delete_original=args.delete)
