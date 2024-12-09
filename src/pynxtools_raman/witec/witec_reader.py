import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union
import numpy as np


logger = logging.getLogger("pynxtools")


def parse_txt_file(self, filepath):
    """
    Read a .txt file from Witec Alpha Raman spectrometer and return a data dictionary
    which contains Raman shift and Intensity
    """
    with open(filepath, "r") as file:
        lines = file.readlines()

    # Initialize dictionaries to hold header and data sections
    header_dict = {}
    data = []
    line_count = 0
    data_mini_header_length = None

    # Track current section
    current_section = None

    for line in lines:
        line_count += 1
        # Remove any leading/trailing whitespace
        line = line.strip()
        # Go through the lines and define two different regions "Header" and
        # "Data", as these need different methods to extract the data.
        if line.startswith("[Header]"):
            current_section = "header"
            continue
        elif line.startswith("[Data]"):
            data_mini_header_length = line_count + 2
            current_section = "data"

            continue

        # Parse the header section
        if current_section == "header" and "=" in line:
            key, value = line.split("=", 1)
            header_dict[key.strip()] = value.strip()

        # Parse the data section
        elif current_section == "data" and "," in line:
            # The header is set excactly until the float-like column data starts
            # Rework this later to extract full metadata
            if line_count <= data_mini_header_length:
                if line.startswith("[Header]"):
                    logger.info(
                        f"[Header] elements in the file {filepath}, are not parsed yet. Consider adden the respective functionality."
                    )
            if line_count > data_mini_header_length:
                values = line.split(",")
                data.append([float(values[0].strip()), float(values[1].strip())])

    # Transform: [[A, B], [C, D], [E, F]] into [[A, C, E], [B, D, F]]
    data = [list(item) for item in zip(*data)]

    # assign column data with keys
    data_dict = {"data/x_values": data[0], "data/y_values": data[1]}
    return data_dict


def post_process_witec(self) -> None:
    """
    Post process the Raman data to add the Raman Shift from input laser wavelength and
    data wavelengths.
    """

    def transform_nm_to_wavenumber(lambda_laser, lambda_measurement):
        stokes_raman_shift = -(
            1e7 / np.array(lambda_measurement) - 1e7 / np.array(lambda_laser)
        )
        # return a list as output
        return stokes_raman_shift.tolist()

    def get_incident_wavelength_from_NXraman():
        substring = "/beam_incident/wavelength"

        # Find matching keys with contain this substring
        wavelength_keys = [key for key in self.eln_data if substring in key]
        # Filter the matching keys for the strings, which contain this substring at the end only
        filtered_list = [
            string for string in wavelength_keys if string.endswith(substring)
        ]
        # get the laser wavelength
        laser_wavelength = self.eln_data.get(filtered_list[0])
        return laser_wavelength

    laser_wavelength = get_incident_wavelength_from_NXraman()

    x_values_raman = transform_nm_to_wavenumber(
        laser_wavelength, self.raman_data["data/x_values"]
    )

    # update the data dictionary
    self.raman_data["data/x_values_raman"] = x_values_raman
