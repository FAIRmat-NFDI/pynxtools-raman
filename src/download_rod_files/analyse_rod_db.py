import os
from pynxtools_raman.rod.rod_reader import RodParser


# Path to the folder
rod_dir = "pynxtools-raman/src/download_rod_files/rod_statistics"


print(os.listdir())

# Get a list of .nxs files in the folder
nxs_files = [file for file in os.listdir(rod_dir) if file.endswith(".rod")]

# Initialize a counter for keys
key_counts = {}


for nxs_file in nxs_files:
    rod = RodParser()
    # read the rod file
    rod.get_cif_file_content(rod_dir + "/" + nxs_file)
    # get the key and value pairs from the rod file
    dict = rod.extract_keys_and_values_from_cif()

    # Iterate through all dictionaries
    for key in dict.keys():
        key_counts[key] = key_counts.get(key, 0) + 1

output_file = "rod_statistics.txt"

# Write to the file
with open(output_file, "w") as file:
    for key, value in key_counts.items():
        file.write(f"{key}\t{value}\n")  # \t for tab spacing

print(f"Data successfully written to {output_file}")
