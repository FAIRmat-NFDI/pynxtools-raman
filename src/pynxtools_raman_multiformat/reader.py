# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""An example reader implementation based on the MultiFormatReader."""

import logging
from typing import Dict, Any
import h5py
import numpy as np

from pynxtools.dataconverter.readers.multi.reader import MultiFormatReader
from pynxtools.dataconverter.readers.utils import parse_yml, parse_flatten_json

import pynxtools_raman_multiformat.reader_rod_utils as pynx_rod

logger = logging.getLogger("pynxtools")

import importlib

CONVERT_DICT = {}


A=parse_flatten_json(self.config_file, create_link_dict=False)
print(A["reader_name"])


sub_reader_paths = {
    "rod": "pynxtools_raman_multiformat.sub_readers.rod.get_data",
    "witec": "pynxtools_raman_multiformat.sub_readers.witec.get_data"
}


# Dynamic input
sub_reader = "rod"  # Can be "farewell" or any other key





class RamanReaderMulti(MultiFormatReader):
    """MyDataReader implementation for the DataConverter to convert mydata to NeXus."""

    supported_nxdls = ["NXraman"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt_data: Dict[str, Any] = {}

        self.extensions = {
            ".yml": self.handle_eln_file,
            ".yaml": self.handle_eln_file,
            ".txt": self.handle_txt_file,
            ".json": self.set_config_file,
            ".rod": self.handle_rod_file}

        self.txt_line_skips = None

    def set_config_file(self, file_path: str) -> Dict[str, Any]:
        if self.config_file is not None:
            logger.info(
                f"Config file already set. Replaced by the new file {file_path}."
            )
        self.config_file = file_path
        return {}

    def handle_eln_file(self, file_path: str) -> Dict[str, Any]:
        self.eln_data = parse_yml(
            file_path,
            convert_dict=CONVERT_DICT,
            parent_key="/ENTRY[entry]",
        )
        #self.txt_line_skips = self.eln_data.get('/ENTRY[entry]/skip')

        return {}
 
    def handle_txt_file(self, filepath) -> Dict[str, Any]:
        self.read_txt_file(filepath)
        return {}

    def handle_rod_file(self, filepath) -> Dict[str, Any]:
        self.read_rod_file(filepath)
        return {}

    def get_attr(self, key: str, path: str) -> Any:
        """
        Get the metadata that was stored in the main(=data) file.
        """

        if self.txt_data is None:
            return None
        return self.txt_data.get(path)

    def read_rod_file(self, filepath):
        # Initiate rod reader as calss
        rod = pynx_rod.RodReader()
        # read the rod file
        rod.get_cif_file_content(filepath)
        # get the key and value pairs from the rod file
        self.rod_data = rod.extract_keys_and_values_from_cif()

    def read_txt_file(self, filepath):
        """
        Read a .txt file from Witec Alpha Raman spectrometer and save the header and measurement data.
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

        #transform linewise read data to colum style data
        data = np.transpose(data)

        # assign column data with keys
        data_dict = {
            "data/x_values": data[:, 0],
            "data/y_values": data[:, 1]
        }

        self.txt_data = data_dict
        self.txt_header = header_dict


    def get_eln_data(self, key: str, path: str) -> Any:
        """
        Returns data from the eln file. This is done via the file: "config_file.json".
        There are two suations:
            1. The .json file has only a key assigned
            2. The .json file has a key AND a value assigned.
        The assigned value should be a "path", which reflects another entry in the eln file.
        This acts as eln_path redirection, which is used for example to assign flexible
        parameters from the eln_file (units, axisnames, etc.)
        """
        if self.eln_data is None:
            return None

        # Use the path to get the eln_data (this refers to the 2. case)
        if len(path) > 0:
            return self.eln_data.get(path)

        # If no path is assigned, use directly the given key to extract
        # the eln data/value (this refers to the 1. case)

        # Filtering list, for NeXus concepts which use mixed notation of
        # upper and lowercase to ensure correct NXclass labeling.
        upper_and_lower_mixed_nexus_concepts = ["/detector_TYPE[",
                                        "/beam_TYPE[",
                                        "/source_TYPE[",
                                        "/polfilter_TYPE[",
                                        "/spectral_filter_TYPE[",
                                        "/temp_control_TYPE[",
                                        "/software_TYPE[",
                                        "/LENS_OPT["

        ]
        if self.eln_data.get(key) is None:
            # filter for mixed concept names
            for string in upper_and_lower_mixed_nexus_concepts:
                key = key.replace(string,"/[")
            # add only characters, if they are lower case and if they are not "[" or "]"
            result = ''.join([char for char in key if not (char.isupper() or char in '[]')])
            # Filter as well for
            result = result.replace("entry",f"ENTRY[{self.callbacks.entry_name}]")

            if self.eln_data.get(result) is not None:
                return self.eln_data.get(result)
            else:
                logger.warning(f"No key found during eln_data processsing for key '{key}' after it's modification to '{result}'.")
        return self.eln_data.get(key)



    # import the correct "get_data_eln" function from the subreader
    if sub_reader in sub_reader_paths:
        module_path, function_name = sub_reader_paths[sub_reader].rsplit('.', 1)
        module = importlib.import_module(module_path)  # Import the module
        get_data = getattr(module, function_name)  # Get the function
    else:
        result = "Unknown action."

    if False:
        def get_data(self, key: str, path: str) -> Any:
            self.handle_eln_file(path)
            return self.rod_data.get(path)


        # the functions below are for the witec eln + txt example
        # Make the get_data function to be depend on input file types,
        # i.e. the function is generalized for all file types. Should
        # import the necessary sub functions from elsewhere depending on input
        def get_data_eln(self, key: str, path: str) -> Any:
            """Returns measurement data from the given eln_data entry."""
            print(self.extensions)
            if path.endswith(("x_values", "y_values","x_values_raman")):
                return self.txt_data.get(f"data/{path}")
            else:
                logger.warning(f"No axis name corresponding to the path {path}.")

    # Restructure the post_process to depend on the given input file
    # i.e. only a single post_process function should be required
    # and the respective subprocessing steps be importet for specified files
    def post_process(self) -> None:
        """
        Post process the Raman data to add the Raman Shift from input laser wavelength and
        data wavelengths.
        """

        def transform_nm_to_wavenumber(self, lambda_laser, lambda_measurement):
            stokes_raman_shift = -(1e7 / lambda_measurement - 1e7 / lambda_laser)
            return stokes_raman_shift

        def get_incident_wavelength_from_NXraman(self):
            substring = "/beam_incident/wavelength"

            # Find matching keys with contain this substring
            wavelength_keys = [key for key in self.eln_data if substring in key]
            # Filter the matching keys for the strings, which contain this substring at the end only
            filtered_list = [string for string in wavelength_keys if string.endswith(substring)]
            # get the laser wavelength
            laser_wavelength = self.eln_data.get(filtered_list[0])
            return laser_wavelength

        laser_wavelength = get_incident_wavelength_from_NXraman(self)
        x_values_raman = transform_nm_to_wavenumber(self, laser_wavelength, self.txt_data["data/x_values"])

        self.txt_data["data/x_values_raman"] = x_values_raman

READER = RamanReaderMulti

# Use this command in this .py file folder:
# dataconverter eln_data.yaml Si-wafer-Raman-Spectrum-1.txt  -c config_file.json --reader raman_multi --nxdl NXraman --output output_raman.nxs
#
# Remaining Warnings
# WARNING: Missing attribute: "/ENTRY[entry]/definition/@URL"
