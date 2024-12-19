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

import copy
import logging
import datetime
from typing import Dict, Any
from pathlib import Path
from typing import Any, Dict, List, Tuple  # Optional, Union, Set
import re

from pynxtools.dataconverter.readers.multi.reader import MultiFormatReader
from pynxtools.dataconverter.readers.utils import parse_yml


from pynxtools_raman.rod.rod_reader import RodParser
from pynxtools_raman.rod.rod_reader import post_process_rod
from pynxtools_raman.witec.witec_reader import post_process_witec
from pynxtools_raman.witec.witec_reader import parse_txt_file


logger = logging.getLogger("pynxtools")

CONVERT_DICT: Dict[str, str] = {}

REPLACE_NESTED: Dict[str, str] = {}


class RamanReader(MultiFormatReader):
    """MyDataReader implementation for the DataConverter to convert mydata to NeXus."""

    supported_nxdls = ["NXraman"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raman_data_dicts: List[Dict[str, Any]] = []
        self.raman_data: Dict[str, Any] = {}
        self.eln_data: Dict[str, Any] = {}
        self.config_file: Path

        self.missing_meta_data = None

        self.extensions = {
            ".yml": self.handle_eln_file,
            ".yaml": self.handle_eln_file,
            ".txt": self.handle_txt_file,
            ".json": self.set_config_file,
            ".rod": self.handle_rod_file,
        }

    def set_config_file(self, file_path: Path) -> Dict[str, Any]:
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

        return {}

    def handle_rod_file(self, filepath) -> Dict[str, Any]:
        # specify default config file for rod files
        reader_dir = Path(__file__).parent
        self.config_file = reader_dir.joinpath("config", "config_file_rod.json")  # pylint: disable=invalid-type-comment

        rod = RodParser()
        # read the rod file
        rod.get_cif_file_content(filepath)
        # get the key and value pairs from the rod file
        self.raman_data = rod.extract_keys_and_values_from_cif()

        if self.raman_data.get("_raman_theoretical_spectrum.intensity"):
            logger.warning(
                f"Theoretical Raman Data .rod file found. File parsing aborted."
            )
            # prevent file parsing to setting an invalid config file name.
            self.config_file = Path()

        # unit_cell_alphabetagamma
        # replace the [ and ] to avoid confliucts in processing with pynxtools NXclass assignments
        self.raman_data = {
            key.replace("_[local]_", "_local_"): value
            for key, value in self.raman_data.items()
        }

        self.missing_meta_data = copy.deepcopy(self.raman_data)

        if self.raman_data.get("_cod_database_code") is not None or "":
            self.raman_data["COD_service_name"] = "Crystallography Open Database"
            del self.missing_meta_data["_cod_database_code"]

        if self.raman_data.get("_cell_length_a") is not None or "":
            # transform 9.40(3) to 9.40
            length_a = re.sub(r"\(\d+\)", "", self.raman_data.get("_cell_length_a"))
            length_b = re.sub(r"\(\d+\)", "", self.raman_data.get("_cell_length_b"))
            length_c = re.sub(r"\(\d+\)", "", self.raman_data.get("_cell_length_c"))
            self.raman_data["rod_unit_cell_length_abc"] = [
                float(length_a),
                float(length_b),
                float(length_c),
            ]
            del self.missing_meta_data["_cell_length_a"]
            del self.missing_meta_data["_cell_length_b"]
            del self.missing_meta_data["_cell_length_c"]
        if self.raman_data.get("_cell_angle_alpha") is not None or "":
            # transform 9.40(3) to 9.40
            angle_alpha = re.sub(
                r"\(\d+\)", "", self.raman_data.get("_cell_angle_alpha")
            )
            angle_beta = re.sub(r"\(\d+\)", "", self.raman_data.get("_cell_angle_beta"))
            angle_gamma = re.sub(
                r"\(\d+\)", "", self.raman_data.get("_cell_angle_gamma")
            )
            self.raman_data["rod_unit_cell_angles_alphabetagamma"] = [
                float(angle_alpha),
                float(angle_beta),
                float(angle_gamma),
            ]
            del self.missing_meta_data["_cell_angle_alpha"]
            del self.missing_meta_data["_cell_angle_beta"]
            del self.missing_meta_data["_cell_angle_gamma"]

        # This changes all uppercase string elements to lowercase string elements for the given key, within a given key value pair
        key_to_make_value_lower_case = "_raman_measurement.environment"
        environment_name_str = self.raman_data.get(key_to_make_value_lower_case)
        if environment_name_str is not None:
            self.raman_data[key_to_make_value_lower_case] = environment_name_str.lower()

        # transform the string into a datetime object
        time_key = "_raman_measurement.datetime_initiated"
        date_time_str = self.raman_data.get(time_key)
        if date_time_str is not None:
            date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")
            # assume UTC for .rod data, as this is not specified in detail
            tzinfo = datetime.timezone.utc
            if isinstance(date_time_obj, datetime.datetime):
                if tzinfo is not None:
                    # Apply the specified timezone to the datetime object
                    date_time_obj = date_time_obj.replace(tzinfo=tzinfo)

                # assign the dictionary the corrrected date format
                self.raman_data[time_key] = date_time_obj.isoformat()

        # remove capitalization
        objective_type_key = "_raman_measurement_device.optics_type"
        objective_type_str = self.raman_data.get(objective_type_key)
        if objective_type_str is not None:
            self.raman_data[objective_type_key] = objective_type_str.lower()
            # set a valid raman NXDL value, but only if it matches one of the correct ones:
            objective_type_list = ["objective", "lens", "glass fiber", "none"]
            if self.raman_data.get(objective_type_key) not in objective_type_list:
                self.raman_data[objective_type_key] = "other"

        self.post_process = post_process_rod.__get__(self, RamanReader)

        return {}

    def handle_txt_file(self, filepath):
        """
        Read a .txt file from Witec Alpha Raman spectrometer and save the header and measurement data.
        """

        # specify default config file
        reader_dir = Path(__file__).parent
        self.config_file = reader_dir.joinpath("config", "config_file_witec.json")  # pylint: disable=invalid-type-comment

        self.raman_data = parse_txt_file(self, filepath)
        self.post_process = post_process_witec.__get__(self, RamanReader)

        return {}

    def get_eln_data(self, key: str, path: str) -> Any:
        """
        Returns data from the eln file. This is done via the file: "config_file.json".
        There are two sitations:
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
        upper_and_lower_mixed_nexus_concepts = [
            "/detector_TYPE[",
            "/beam_TYPE[",
            "/source_TYPE[",
            "/polfilter_TYPE[",
            "/spectral_filter_TYPE[",
            "/temp_control_TYPE[",
            "/software_TYPE[",
            "/LENS_OPT[",
        ]
        if self.eln_data.get(key) is None:
            # filter for mixed concept names
            for string in upper_and_lower_mixed_nexus_concepts:
                key = key.replace(string, "/[")
            # add only characters, if they are lower case and if they are not "[" or "]"
            result = "".join(
                [char for char in key if not (char.isupper() or char in "[]")]
            )
            # Filter as well for
            result = result.replace("entry", f"ENTRY[{self.callbacks.entry_name}]")

            if self.eln_data.get(result) is not None:
                return self.eln_data.get(result)
            else:
                logger.warning(
                    f"No key found during eln_data processsing for key '{key}' after it's modification to '{result}'."
                )
        return self.eln_data.get(key)

    def get_data(self, key: str, path: str) -> Any:
        """
        Returns the data from a .rod file (Raman Open Database), which was trasnferred into a dictionary.
        """

        value = self.raman_data.get(path)

        # this filters out the meta data, which is up to now only created for .rod files

        if (path is None or path is "") and key is not None:
            return self.raman_data.get(key)

        if self.missing_meta_data:
            # this if condition is required, to only delete keys which are abaialble by the data.
            # e.g. is defined to extract it via config.json, but there is no value in meta data
            if path in self.missing_meta_data.keys():
                del self.missing_meta_data[path]

        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return self.raman_data.get(path)
        else:
            logger.warning(f"No axis name corresponding to the path {path}.")

    def read(
        self,
        template: dict = None,
        file_paths: Tuple[str] = None,
        objects: Tuple[Any] = None,
        **kwargs,
    ) -> dict:
        template = super().read(template, file_paths, objects, suppress_warning=True)
        # set default data

        if self.missing_meta_data:
            for key in self.missing_meta_data:
                template[
                    f"/ENTRY[{self.callbacks.entry_name}]/COLLECTION[unused_rod_keys]/{key}"
                ] = f"{self.missing_meta_data[key]}"

        template["/@default"] = "entry"

        return template


READER = RamanReader
