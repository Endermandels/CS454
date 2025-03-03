import os
import glob
import shutil

def remove_dat_files():
    # Get the list of all .dat files in the current directory
    dat_files = glob.glob("*.dat")

    # Remove each .dat file
    for file in dat_files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")

def remove_docs():
    fn = 'docs'
    cwd = os.getcwd()
    path = os.path.join(cwd, fn)
    # Check if the "docs" folder exists
    if os.path.exists(path) and os.path.isdir(path):
        try:
            # Remove all contents of the "docs" folder
            shutil.rmtree(path)
            print(f"Removed all contents in: {path}")
        except Exception as e:
            print(f"Error removing {path}: {e}")
    else:
        print(f"'{path}' folder does not exist or is not a directory.")

if __name__ == "__main__":
    if input('Will delete all save data. Continue? (Y/n) ').lower() == 'y':
        remove_dat_files()
        remove_docs()
