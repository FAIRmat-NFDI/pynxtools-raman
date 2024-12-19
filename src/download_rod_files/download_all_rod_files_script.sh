#!/bin/bash

# Define your input file
input_file="src/download_rod_files/ROD-numbers_subset_test.txt"
# Change it to this line, to download all .rod files.
#input_file="src/download_rod_files/ROD-numbers.txt" # took 7 minutes to download all files

# Ask for confirmation before proceeding
read -p "Are you sure you want to proceed with the download? (y/n): " confirmation

# Check user input
if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
  echo "Operation cancelled."
  exit 1
fi


# Read all numbers from the file
while read -r num; do
  # Loop over your desired range
  download_rod_file "$num"
done < "$input_file"