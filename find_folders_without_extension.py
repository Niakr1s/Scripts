import os
import argparse

def find_folders_without_extension(root_folder, extension):
    """
    Find subfolders that don't contain at least one file with the given extension.
    
    Args:
        root_folder (str): Path to the root folder to search
        extension (str): File extension to look for (e.g., '.txt', '.py')
    
    Returns:
        list: List of folder paths without files of the specified extension
    """
    folders_without_extension = []
    
    # Ensure extension starts with a dot
    if not extension.startswith('.'):
        extension = '.' + extension
    
    try:
        for dirpath, dirnames, filenames in os.walk(root_folder):
            # Check if any file in current directory has the specified extension
            has_file_with_extension = any(
                filename.lower().endswith(extension.lower()) 
                for filename in filenames
            )
            
            # If no file with the extension is found, and this is not the root folder
            if not has_file_with_extension and dirpath != root_folder:
                folders_without_extension.append(dirpath)
                
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except Exception as e:
        print(f"Error processing directory: {e}")
    
    return folders_without_extension

def main():
    parser = argparse.ArgumentParser(
        description="List subfolders that don't contain at least one file with a given extension"
    )
    parser.add_argument(
        "folder_path", 
        help="Path to the root folder to search"
    )
    parser.add_argument(
        "extension", 
        help="File extension to look for (e.g., txt, py, pdf)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate folder path
    if not os.path.exists(args.folder_path):
        print(f"Error: Folder '{args.folder_path}' does not exist.")
        return
    
    if not os.path.isdir(args.folder_path):
        print(f"Error: '{args.folder_path}' is not a directory.")
        return
    
    # Find folders without the specified extension
    folders = find_folders_without_extension(args.folder_path, args.extension)
    
    # Display results
    if folders:
        print(f"Subfolders without any '{args.extension}' files:")
        for folder in sorted(folders):
            print(folder)
        if args.verbose:
            print(f"\nTotal: {len(folders)} folders found")
    else:
        print(f"No subfolders found without '{args.extension}' files.")

if __name__ == "__main__":
    main()