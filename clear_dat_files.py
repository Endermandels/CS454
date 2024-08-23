import os
import glob

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

if __name__ == "__main__":
    remove_dat_files()
