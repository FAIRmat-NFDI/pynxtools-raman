#!/bin/bash

# Define the folder containing the .rod files
folder_path="." # took about 8min

# Loop over all .rod files in the folder
for file in "$folder_path"/*.rod; do
    # Extract the base name (without extension)
    base_name=$(basename "$file" .rod)
    
    # Execute the command with the base name
    dataconverter "$file" src/pynxtools_raman/config/config_file_rod.json \
      --reader raman --nxdl NXraman --output "${base_name}.nxs"
done