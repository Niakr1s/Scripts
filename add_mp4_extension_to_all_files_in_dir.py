import os
import sys


def add_mp4_extension(directory_path):
    """
    Adds .mp4 extension to all files in the specified directory.

    Args:
        directory_path (str): Path to the directory containing files
    """
    try:
        # Check if directory exists
        if not os.path.isdir(directory_path):
            print(f"Error: Directory '{directory_path}' does not exist.")
            return

        # Get all files in the directory (excluding subdirectories)
        files = [
            f
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))
        ]

        if not files:
            print("No files found in the directory.")
            return

        renamed_count = 0

        for filename in files:
            # Skip files that already have .mp4 extension
            if filename.lower().endswith(".mp4"):
                print(f"Skipping '{filename}' - already has .mp4 extension")
                continue

            # Construct new filename with .mp4 extension
            new_filename = filename + ".mp4"
            old_path = os.path.join(directory_path, filename)
            new_path = os.path.join(directory_path, new_filename)

            # Check if target file already exists
            if os.path.exists(new_path):
                print(
                    f"Warning: '{new_filename}' already exists. Skipping '{filename}'"
                )
                continue

            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: '{filename}' -> '{new_filename}'")
            renamed_count += 1

        print(f"\nOperation completed. {renamed_count} files were renamed.")

    except PermissionError:
        print(
            "Error: Permission denied. Make sure you have write access to the directory."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to handle user input and execute the renaming operation.
    """
    # If directory path is provided as command line argument
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        # Ask user for directory path
        directory_path = input("Enter the directory path: ").strip()

    # Remove quotes if present (common when copying paths)
    directory_path = directory_path.strip("\"'")

    # Confirm with user before proceeding
    print(f"\nThis will add '.mp4' extension to all files in: {directory_path}")
    print("Files that already have .mp4 extension will be skipped.")
    confirmation = input("Do you want to continue? (y/n): ").strip().lower()

    if confirmation in ["y", "yes"]:
        add_mp4_extension(directory_path)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
