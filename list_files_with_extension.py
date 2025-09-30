#!/usr/bin/env python3
"""
File Lister Script
Lists all files with a given extension, with options to hide extensions and control subfolder depth.
"""

import argparse
import os
import sys
from pathlib import Path

def list_files_with_extension(directory, extension, hide_extension=False, max_depth=0, current_depth=0):
    """
    Recursively list files with given extension up to specified depth.
    
    Args:
        directory (str): Starting directory
        extension (str): File extension to search for (without dot)
        hide_extension (bool): Whether to hide file extensions in output
        max_depth (int): Maximum subfolder depth to search (0 = current directory only)
        current_depth (int): Current depth in recursion (internal use)
    
    Returns:
        list: Sorted list of file paths
    """
    files_found = []
    
    try:
        for item in Path(directory).iterdir():
            if item.is_file():
                if item.suffix.lower() == f".{extension.lower()}":
                    if hide_extension:
                        # Remove the extension from the filename
                        file_path = str(item.stem)
                    else:
                        file_path = str(item.name)
                    files_found.append(file_path)
            
            elif item.is_dir() and current_depth < max_depth:
                # Recursively search subdirectories if within depth limit
                subdir_files = list_files_with_extension(
                    str(item), extension, hide_extension, max_depth, current_depth + 1
                )
                files_found.extend(subdir_files)
                
    except PermissionError:
        print(f"Warning: Permission denied accessing {directory}", file=sys.stderr)
    except Exception as e:
        print(f"Error accessing {directory}: {e}", file=sys.stderr)
    
    return files_found

def main():
    parser = argparse.ArgumentParser(
        description="List files with given extension in alphabetical order",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s . py                    # List all Python files in current directory
  %(prog)s . txt -h                # List txt files, hide extensions
  %(prog)s . jpg -d 2             # List jpg files up to 2 subfolder levels deep
  %(prog)s /path/to/folder pdf -d 1 -h  # Multiple options combined
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory to search in (default: current directory)',
        nargs='?',
        default='.'
    )
    
    parser.add_argument(
        'extension',
        help='File extension to search for (without dot, e.g., "txt" not ".txt")'
    )
    
    parser.add_argument(
        '-e', '--hide-extension',
        dest='hide_extension',
        action='store_true',
        help='Hide file extensions in output'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=0,
        help='Subfolder depth (0=current dir only, 1=one level deep, etc.) Default: 0',
        metavar='DEPTH'
    )
    
    args = parser.parse_args()
    
    # Validate directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Validate depth is non-negative
    if args.depth < 0:
        print("Error: Depth must be a non-negative integer", file=sys.stderr)
        sys.exit(1)
    
    # Remove leading dot from extension if provided
    extension = args.extension.lstrip('.')
    
    # Get and sort files
    files = list_files_with_extension(
        args.directory,
        extension,
        args.hide_extension,
        args.depth
    )
    
    files.sort()  # Alphabetical order
    
    # Display results
    if files:
        for file_path in files:
            print(file_path)

if __name__ == "__main__":
    main()