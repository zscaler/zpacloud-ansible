import os
import chardet


def convert_to_utf8(filename):
    """Convert a file to UTF-8 encoding."""
    # Detect encoding
    with open(filename, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        current_encoding = result["encoding"]

    # Read in current encoding
    with open(filename, "r", encoding=current_encoding) as file:
        content = file.read()

    # Write in UTF-8 encoding
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def convert_directory_to_utf8(directory):
    """Convert all files in a directory (and its subdirectories) to UTF-8."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                convert_to_utf8(file_path)
                print(f"Converted {file_path} to UTF-8")
            except Exception as e:
                print(f"Failed to convert {file_path}: {e}")


# Replace 'path/to/your/directory' with the path to your modules/plugins directory
directory_path = "./plugins/modules"
convert_directory_to_utf8(directory_path)
