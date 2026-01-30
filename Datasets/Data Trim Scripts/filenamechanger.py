import os
import re

def rename_files():
    # Get the directory where the script is currently located
    directory = os.path.dirname(os.path.abspath(__file__))
    
    # Pattern to match: Status_Penmanshiel_(number)_YYYY-MM-DD_-_YYYY-MM-DD_XXXX.csv
    # This captures the number (group 1)
    pattern = re.compile(r'Status_Penmanshiel_(\d+)_.*\.csv')

    print(f"Checking files in: {directory}")

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            # Extract the number from the first capture group
            file_number = match.group(1)
            
            # Construct the new filename
            new_name = f"Penmanshiel_{file_number}_2016.csv"
            
            # Define full paths
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_name)

            # Perform the rename
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    rename_files()