import sys


def find_duplicate_lines(filename):
    """
    Find and display duplicate lines in a text file (case-sensitive)
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Remove newline characters and count occurrences
        line_counts = {}
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                line_counts[line] = line_counts.get(line, 0) + 1

        # Find duplicates
        duplicates = {line: count for line, count in line_counts.items() if count > 1}

        return duplicates

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}


def main():
    filename = sys.argv[1]
    duplicates = find_duplicate_lines(filename)

    if duplicates:
        print("\nDuplicate lines found:")
        print("-" * 40)
        for line, count in duplicates.items():
            print(f"'{line}' - appears {count} times")
    else:
        print("No duplicate lines found.")


if __name__ == "__main__":
    main()
