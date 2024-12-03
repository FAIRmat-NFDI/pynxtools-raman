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
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pynxtools.dataconverter.readers.multi.reader import MultiFormatReader
from pynxtools.dataconverter.readers.utils import parse_yml, parse_flatten_json

import pynxtools_raman_multiformat.reader_rod_utils as pynx_rod


#from pynxtools_raman_multiformat.sub_readers.witec import MapperWitec
from pynxtools_raman_multiformat.witec.witec_reader import MapperWitec
from pynxtools_raman_multiformat.rod.rod_reader import MapperRod

logger = logging.getLogger("pynxtools")

import importlib

CONVERT_DICT = {}

REPLACE_NESTED: Dict[str, str] = {}


class RamanReaderMulti(MultiFormatReader):
    """MyDataReader implementation for the DataConverter to convert mydata to NeXus."""

    supported_nxdls = ["NXraman"]


    reader_dir = Path(__file__).parent
    config_file: Optional[Union[str, Path]] = reader_dir.joinpath(
        "config", "template.json"
    )


    __prmt_file_ext__ = [ 
        ".rod",
    ]

    __vendors__ = ["witec", "rod"]
    __prmt_vndr_cls: Dict[str, Dict] = {
        ".rod": {"raman_open_database": MapperRod},#add the classes
        ".txt": {"witec_alpha": MapperWitec},
    }


    __file_err_msg__ = ("Need an Raman data file with one of the following extensions: "        f"{__prmt_file_ext__}")
    __vndr_err_msg__ = ("Need an XPS data file from one of the following vendors: " f"{__vendors__}")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raman_data_dicts: List[Dict[str, Any]] = []
        self.raman_data: Dict[str, Any] = {}
        self.eln_data: Dict[str, Any] = {}



        self.reader_type: str = {}
        self.txt_line_skips = None
        self.data_file_path = ""
        self.sub_reader_name = None

        self.extensions = {
            ".yml": self.handle_eln_file,
            ".yaml": self.handle_eln_file,
            ".txt": self.handle_txt_file,
            ".json": self.set_config_file,
            ".rod": self.handle_rod_file}

        for ext in RamanReaderMulti.__prmt_file_ext__:
            self.extensions[ext] = self.handle_data_file


    def set_config_file(self, file_path: str) -> Dict[str, Any]:
        if self.config_file is not None:
            logger.info(
                f"Config file already set. Replaced by the new file {file_path}."
            )
        self.config_file = file_path
        return {}



    #adjust the code with respect to Raman data
    def handle_eln_file(self, file_path: str) -> Dict[str, Any]:
        """
        Loads ELN file and handles specific cases.
        """

        def combine_and_unique_string(string: str, elements: List[str]) -> str:
            """
            Combines a comma-separated string and a list into a single string with unique elements.

            Args:
                string (str): A comma-separated string.
                elements (list): A list of elements to combine with the string.

            Returns:
                str: A comma-separated string with unique elements.
            """
            existing_elements = [
                item.strip() for item in string.split(",") if item.strip()
            ]
            combined_elements = list(set(existing_elements + elements))
            combined_elements.sort()
            return ", ".join(combined_elements)

        eln_data = parse_yml(
            file_path,
            convert_dict=CONVERT_DICT,
            replace_nested=REPLACE_NESTED,
            parent_key="/ENTRY",
        )

        # replace paths for entry-specific ELN data
        pattern = re.compile(r"(/ENTRY)/ENTRY(\[[^\]]+\])")

        formula_keys = ("molecular_formula_hill", "chemical_formula")

        initial_eln_keys = list(eln_data.keys())

        for key, value in eln_data.copy().items():
            new_key = pattern.sub(r"\1\2", key)

            # Parse substance/molecular_formula_hill and chemical_formula into atom_types
            for form_key in formula_keys:
                if form_key in key:
                    atom_types = list(extract_atom_types(value))

                    if atom_types:
                        modified_key = re.sub(r"SUBSTANCE\[.*?\]/", "", key)
                        modified_key = modified_key.replace(form_key, "atom_types")

                        if modified_key not in initial_eln_keys:
                            if modified_key not in self.eln_data:
                                self.eln_data[modified_key] = ", ".join(atom_types)
                            else:
                                self.eln_data[modified_key] = combine_and_unique_string(
                                    self.eln_data[modified_key], atom_types
                                )
                        else:
                            logger.info(
                                f"{key} from ELN was not parsed to atom_types because {modified_key} already exists."
                            )

            if isinstance(value, datetime.datetime):
                eln_data[key] = value.isoformat()

            self.eln_data[new_key] = eln_data.pop(key)

        return {}


    def handle_data_file(self, file_path: str) -> Dict[str, Any]:
        def _check_for_vendors(file_path: str) -> str:
            """
            Check for the vendor name of the Raman data file.

            """
            _, file_ext = os.path.splitext(file_path)

            vendor_dict = RamanReaderMulti.__prmt_vndr_cls[file_ext]

            if len(vendor_dict) == 1:
                return list(vendor_dict.keys())[0]
            if file_ext == ".txt":
                return _check_for_vendors_txt(file_path)
            return None

        def _check_for_vendors_txt(file_path: str) -> str:
            """
            Search for a vendor names in a txt file

            Parameters
            ----------
            file : str
                XPS txt file.

            Returns
            -------
            vendor
                Vendor name if that name is in the txt file.

            """
            vendor_dict = RamanReaderMulti.__prmt_vndr_cls[".txt"]

            with open(file_path, encoding="utf-8") as txt_file:
                contents = txt_file.read()

            for vendor in vendor_dict:
                vendor_options = [vendor, vendor.upper(), vendor.capitalize()]

                if any(vendor_opt in contents for vendor_opt in vendor_options):
                    return vendor
                if contents[:6] == "[Info]":
                    # This is for picking the Scienta reader is "scienta"
                    # is not in the file
                    return vendor
            return "unknown"

        _, file_ext = os.path.splitext(file_path)

        if file_ext in RamanReaderMulti.__prmt_file_ext__:
            vendor = _check_for_vendors(file_path)
            try:
                #select the respective parser from fileinput
                parser = RamanReaderMulti.__prmt_vndr_cls[file_ext][vendor]()

                #perform the parse file action from the sub parser
                parser.parse_file(file_path, **self.kwargs)
                self.config_file = RamanReaderMulti.reader_dir.joinpath(
                    "config", parser.config_file
                )
                data_dict = parser.data_dict

            except ValueError as val_err:
                raise ValueError(RamanReaderMulti.__vndr_err_msg__) from val_err
            except KeyError as key_err:
                raise KeyError(RamanReaderMulti.__vndr_err_msg__) from key_err
        else:
            raise ValueError(RamanReaderMulti.__file_err_msg__)

        self.raman_data_dicts += [data_dict]

        return {}


    def get_entry_names(self) -> List[str]:
        """
        Returns a list of entry names which should be constructed from the data.
        Defaults to creating a single entry named "entry".
        """
        # Track entries for using for eln data
        entries: List[str] = []

        try:
            for entry in self.raman_data["data"]:
                entries += [entry]
        except KeyError:
            pass

        if not entries:
            entries += ["entry"]

        return list(dict.fromkeys(entries))

    def setup_template(self) -> Dict[str, Any]:
        """
        Setups the initial data in the template.
        """
        # TODO: Set fixed information, e.g., about the reader.
        return {}

    def handle_objects(self, objects: Tuple[Any]) -> Dict[str, Any]:
        """
        Handles the objects passed into the reader.
        """
        return {}

    def post_process(self) -> None:
        """
        Do postprocessing after all files and the config file are read .
        """
        #self._combine_datasets()

        # TODO: make processing of multiple entities robust
        # self.process_multiple_entities()


    def process_multiple_entities(self) -> None:
        """
        Check if there are multiple of some class and, if so, change the
        keys and values in the config file.

        This replaces all occureces of "detector" and "electronanalyser"
        in the config dict by the respective names (e.g., detector0, detector1)
        and removes the generic term if there are multiple different instances.

        """
        multiples_to_check = {
            "electronanalyser": self._get_analyser_names,
            "detector": self._get_detector_names,
        }

        """
        Currently, it only works if the config_dict is loaded BEFORE the
        parse_json_config method".

        In principle, the same replacement should be done for the eln and
        (meta)data dicts.
        """

        for config_key, config_value in self.config_dict.copy().items():
            for original_key, search_func in multiples_to_check.items():
                entity_names = search_func()

                if len(entity_names) >= 1 and entity_names[0] is not original_key:
                    for name in entity_names:
                        modified_value = copy.deepcopy(config_value)

                        modified_key = config_key.replace(
                            f"[{original_key}]",
                            f"[{name}]",
                        )

                        if (
                            isinstance(config_value, str)
                            and f"{original_key}/" in config_value
                        ):
                            modified_value = config_value.replace(
                                f"{original_key}/", f"{name}/"
                            )

                        self.config_dict[modified_key] = modified_value
                        del self.config_dict[config_key]

    def get_metadata(
        self,
        metadata_dict: Dict[str, Any],
        path: str,
        entry_name: str,
    ) -> Any:
        """
        Get metadata from the ELN or XPS data dictionaries.

        Note that the keys of metadata_dict may contain more than
        the path, i.e.,
        /ENTRY[my-entry]/instrument/analyser/collectioncolumn/voltage.
        With the regex, the path = "collectioncolumn/voltage" would
        still yield the correct value.

        Parameters
        ----------
        metadata_dict : Dict[str, Any]
            One of ELN or XPS data dictionaries .
        path : str
            Path to search in the metadata_dict
        entry_name : str
            Entry name to search.

        Yields
        ------
        value: Any
            The value in the metadata_dict.

        """
        pattern = re.compile(
            rf"^/ENTRY\[{re.escape(entry_name)}\](?:/.*/|/){re.escape(path)}$"
        )

        matching_key = next((key for key in metadata_dict if pattern.match(key)), None)

        value = metadata_dict.get(matching_key)

        if value is None or str(value) == "None":
            return

        if isinstance(value, datetime.datetime):
            value = value.isoformat()

        return value

    def get_attr(self, key: str, path: str) -> Any:
        """
        Get the metadata that was stored in the main file.
        """
        return self.get_metadata(self.raman_data, path, self.callbacks.entry_name)

    def get_eln_data(self, key: str, path: str) -> Any:
        """
        Returns data from the given eln path.
        Gives preference to ELN data for a given entry before searching
        the ELN data for all entries.
        Returns None if the path does not exist.
        """
        if key in self.eln_data:
            return self.eln_data.get(key)

        else:
            # check for similar key with generic /ENTRY/
            pattern = re.compile(r"(/ENTRY)\[[^\]]+\]")
            modified_key = pattern.sub(r"\1", key)
            if modified_key in self.eln_data:
                return self.eln_data.get(modified_key)
        return

    def get_data_dims(self, key: str, path: str) -> List[str]:
        """
        Returns the dimensions of the data from the given path.
        """

        def get_signals(key: str) -> List[str]:
            xr_data = self.raman_data["data"].get(f"{self.callbacks.entry_name}")

            if key == "scans":
                data_vars = _get_scan_vars(xr_data.data_vars)
            elif key == "channels":
                data_vars = _get_channel_vars(xr_data.data_vars)
                if not data_vars:
                    data_vars = _get_scan_vars(xr_data.data_vars)
            else:
                data_vars = [""]

            return list(map(str, data_vars))

        if path.startswith("@data:*"):
            return get_signals(key=path.split(":*.")[-1])

        if any(x in path for x in ["counts", "raw/@units"]):
            return get_signals(key="channels")

        return get_signals(key="scans")

    def get_data(self, key: str, path: str) -> Any:
        """
        Returns data for a given key.
        Can either return averaged, scan, or channel data.
        Should return None if the path does not exist.
        """

        xr_data = self.raman_data["data"].get(f"{self.callbacks.entry_name}")

        if path.endswith("average"):
            return np.mean(
                [xr_data[x_arr].data for x_arr in _get_scan_vars(xr_data.data_vars)],
                axis=0,
            )

        elif path.endswith("errors"):
            return np.std(
                [xr_data[x_arr].data for x_arr in _get_scan_vars(xr_data.data_vars)],
                axis=0,
            )

        elif path.endswith("raw_data"):
            data_vars = _get_channel_vars(xr_data.data_vars)

            if not data_vars:
                # If there is no channel data, use scan data.
                data_vars = _get_scan_vars(xr_data.data_vars)

            # Skip average cycle data
            return np.array(
                [
                    xr_data[data_var].data
                    for data_var in data_vars
                    if SCAN_COUNT in data_var
                ]
            )

        elif path.endswith("scans"):
            return np.array(xr_data[path.split(".scans")[0]])

        elif path.endswith("channels"):
            return np.array(xr_data[path.split(".channels")[0]])

        elif "energy" in path:
            return np.array(xr_data.coords["energy"].values)

        else:
            try:
                return xr_data[path]
            except KeyError:
                try:
                    return np.array(xr_data.coords[path].values)
                except KeyError:
                    pass

    def set_root_default(self, template):
        """Set the default for automatic plotting."""
        survey_count_ = 0
        count = 0

        for entry in self.get_entry_names():
            if "Survey" in entry and survey_count_ == 0:
                survey_count_ += 1
                template["/@default"] = entry

            # If no Survey set any scan for default
            if survey_count_ == 0 and count == 0:
                count += 1
                template["/@default"] = entry

    def read(
        self,
        template: dict = None,
        file_paths: Tuple[str] = None,
        objects: Tuple[Any] = None,
        **kwargs,
    ) -> dict:
        template = super().read(template, file_paths, objects, suppress_warning=True)
        self.set_root_default(template)

        final_template = Template()
        for key, val in template.items():
            if val is not None:
                if "@units" in key:
                    check_units(key, val)
                final_template[key] = val

        return final_template







    def handle_txt_file(self, filepath) -> Dict[str, Any]:
        self.data_file_path = filepath
        self.read_txt_file(filepath)
        return {}

    def handle_rod_file(self, filepath) -> Dict[str, Any]:
        self.post_process = post_process_rod
        self.get_data = get_data_rod
        self.get_attr = get_attr_rod































































































    # code below is from the old version
    if False:
        def get_subreader_from_config(self, file_path: str) -> Dict[str, Any]:
            if file_path is not None:
                config_file_for_subreader_name = parse_flatten_json(
                    self.config_file, create_link_dict=False
                )

            self.sub_reader_name = config_file_for_subreader_name.get("/ENTRY[entry]/PROGRAM[pynxtools_raman_sub_reader]/program")

            return self.sub_reader_name


        def handle_eln_file(self, file_path: str) -> Dict[str, Any]:
            self.eln_data = parse_yml(
                file_path,
                convert_dict=CONVERT_DICT,
                parent_key="/ENTRY[entry]",
            )
            #self.txt_line_skips = self.eln_data.get('/ENTRY[entry]/skip')

            return {}

        def handle_txt_file(self, filepath) -> Dict[str, Any]:
            self.data_file_path = filepath
            self.read_txt_file(filepath)
            return {}


        def handle_rod_file(self, filepath) -> Dict[str, Any]:
            self.post_process = post_process_rod
            self.get_data = get_data_rod
            self.get_attr = get_attr_rod

            self.read_rod_file(filepath)
            return {}




        # if all these functions are renamed, the process does not work again.
        def get_data_A(self, key: str, path: str) -> Any:
            """
            Returns the data from a .rod file (Raman Open Database), which was trasnferred into a dictionary.
            """
            print(self.raman_data.get(path))
            try:
                return float(self.raman_data.get(path))
            except:
                return self.raman_data.get(path)


        def get_attr_A(self, key: str, path: str) -> Any:
            """
            Get the metadata that was stored in the main(=data) file.
            """
            return None

        def post_process_A() -> None:
            """
            Post process the Raman data to add the Raman Shift from input laser wavelength and
            data wavelengths.
            """
            return {}




        def get_data_rod(self, key: str, path: str) -> Any:
            """
            Returns the data from a .rod file (Raman Open Database), which was trasnferred into a dictionary.
            """
            print("###################################")
            try:
                return float(self.raman_data.get(path))
            except:
                return self.raman_data.get(path)


        def get_attr_rod(self, key: str, path: str) -> Any:
            """
            Get the metadata that was stored in the main(=data) file.
            """
            return None

        def post_process_rod() -> None:
            """
            Post process the Raman data to add the Raman Shift from input laser wavelength and
            data wavelengths.
            """
            return {}


















    if False:
        def handle_rod_file(self, filepath) -> Dict[str, Any]:

            # Get the subreader name
            sub_reader_name = self.get_subreader_from_config(self.config_file)

            if sub_reader_name not in sub_reader_paths.keys():
                raise ValueError

            self.get_data = self.get_datas.get(sub_reader_name, self.get_data)
            self.get_attr = self.get_attrs.get(sub_reader_name, self.get_attr)
            self.post_process = self.post_processes.get(sub_reader_name, self.post_process)

            self.read_rod_file(filepath)
            return {}

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

        self.raman_data = data_dict
        #header dict is not assigned here
        #self.raman_data = header_dict

    def read_rod_file(self, filepath):
        # Initiate rod reader as calss
        rod = pynx_rod.RodReader()
        # read the rod file
        rod.get_cif_file_content(filepath)
        # get the key and value pairs from the rod file
        self.raman_data = rod.extract_keys_and_values_from_cif()

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


    if False:
        def _import_functions(self):

            if self.sub_reader_name is None:
                raise ValueError

            module_path = sub_reader_paths[self.sub_reader_name]
            module = importlib.import_module(module_path)  # Import the module

            get_data = getattr(module, "get_data")  # Get the function
            get_attr = getattr(module, "get_attr")
            post_process = getattr(module, "post_process")

            return get_data, get_attr, post_process









    if False:
        if sub_reader_name in sub_reader_paths:
            if sub_reader_name is None:
                raise ValueError
            module_path = sub_reader_paths[sub_reader_name]
            get_data_function_name = "get_data"
            module = importlib.import_module(module_path)  # Import the module
            get_data = getattr(module, get_data_function_name)  # Get the function
        else:
            result = "Unknown action."

        # import the correct "get_attr" function from the subreader
        if sub_reader_name in sub_reader_paths:
            module_path = sub_reader_paths[sub_reader_name]
            get_attr_function_name = "get_attr"
            module = importlib.import_module(module_path)  # Import the module
            get_attr = getattr(module, get_attr_function_name)  # Get the function
        else:
            result = "Unknown action."

        # import the correct "post_process" function from the subreader
        if sub_reader_name in sub_reader_paths:

            module_path = sub_reader_paths[sub_reader_name]
            post_process_function_name = "post_process"
            module = importlib.import_module(module_path)  # Import the module
            post_process = getattr(module, post_process_function_name)  # Get the function
        else:
            result = "Unknown action."


READER = RamanReaderMulti

# Use this command in this .py file folder:
# dataconverter eln_data.yaml Si-wafer-Raman-Spectrum-1.txt  -c config_file.json --reader raman_multi --nxdl NXraman --output output_raman.nxs
#
# Remaining Warnings
# WARNING: Missing attribute: "/ENTRY[entry]/definition/@URL"
