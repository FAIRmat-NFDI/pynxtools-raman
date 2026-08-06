#
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
import copy
import datetime
import logging
import re
from pathlib import Path
from typing import Any

import gemmi  # for cif file handling

from pynxtools_raman.parsers.base import _RamanParser

logger = logging.getLogger("pynxtools")

__all__ = ["RodParser", "build_citation_fields"]

ROD_CITATION_DOI = "10.1107/S1600576719004229"
ROD_CITATION_TEXT = (
    "El Mendili, Y. et al. (2019). Raman Open Database: first interconnected "
    "Raman-X-ray diffraction open-access resource for material identification. "
    f"J. Appl. Cryst. 52, 618-625. https://doi.org/{ROD_CITATION_DOI}"
)
ROD_LICENSE_TEXT = (
    "Released under the CC0 1.0 Universal Public Domain Dedication "
    "(https://creativecommons.org/publicdomain/zero/1.0/)."
)
ROD_RECORD_URL_TEMPLATE = "https://solsa.crystallography.net/rod/{code}.html"

# The two CIF keys that hold the actual measured spectrum, as opposed to
# metadata about it - everything else extracted from the .rod file is a
# scalar attribute of the measurement, not measurement data itself.
ROD_SPECTRUM_DATA_KEYS = ("_raman_spectrum.intensity", "_raman_spectrum.raman_shift")


class RodParser(_RamanParser):
    """
    Parses .rod files (CIF-formatted records from the Raman Open Database)
    via "get_cif_file_content" / "extract_keys_and_values_from_cif", then
    splits the result into scalar metadata (self.attrs) and the measured
    spectrum arrays (self.data).
    """

    supported_file_extensions = (".rod",)
    config_file = "config_file_rod.json"
    unused_attrs_group_name = "unused_rod_keys"

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.cif_doc = None
        self.cif_block = None
        self.lines = []

    def matches_file(self, file: Path) -> bool:
        """A .rod file is a CIF file, and every CIF file must declare a
        single data block near the top via a `data_<name>` line."""
        try:
            with open(file, encoding="utf-8") as rod_file:
                for _, line in zip(range(50), rod_file):
                    if line.startswith("data_"):
                        return True
        except OSError:
            return False
        return False

    def _read_lines(self, file: str | Path):
        """
        Read all lines from the input files.
        """
        with open(file, encoding="utf-8") as utf8_file:
            lines = utf8_file.readlines()

        return lines

    def get_cif_file_content(self, file_path):
        doc = gemmi.cif.read_file(str(file_path))
        block = doc.sole_block()  # extract main block of cif file
        self.cif_doc = doc
        self.cif_block = block
        self.lines = self._read_lines(file_path)

    def get_string_position(self, string_element: str, check_only_pos_zero=False):
        line_positions_of_str_element = []

        rod_lines = self.lines
        if check_only_pos_zero:
            for line_number, lines in enumerate(rod_lines):
                if string_element in lines[0]:
                    line_positions_of_str_element.append(line_number)
        else:
            if rod_lines is None:
                logger.info(f"Problem during reading .rod file. 'rod_lines' is None.")
            else:
                for line_number, lines in enumerate(rod_lines):
                    if string_element in lines:
                        line_positions_of_str_element.append(line_number)
        return line_positions_of_str_element

    def get_keys_and_loop_boolean(self, key_positions, key_pos_in_loops):
        cif_key_loop_boolean_dict = {}
        for key_pos in key_positions:
            # go through all key_positions (i.e. line number)
            # and check two cases: These lines are part of a loop or
            # they are not part of a loop
            # If they are in a loop, assign the bool value required for read
            # out of the value from the key (i.e set =True)
            if key_pos in key_pos_in_loops:
                # remove linebreaks to ensure right assignment in values for input keys
                cif_key_loop_boolean_dict[self.lines[key_pos].replace("\n", "")] = True
            if key_pos not in key_pos_in_loops:
                # some keys have their values on the same line, some on other lines
                # Extract only the key, as this is always available.
                # Use the key later to get the respective values
                if " " in self.lines[key_pos]:
                    key, value = self.lines[key_pos].split(maxsplit=1)
                    cif_key_loop_boolean_dict[key] = False
                else:
                    # If only the key is on the line, without its value, extract only the key,
                    # Remove possible linebreaks for clarity with .replace()
                    cif_key_loop_boolean_dict[self.lines[key_pos].replace("\n", "")] = (
                        False
                    )

        if len(key_positions) == len(cif_key_loop_boolean_dict):
            return cif_key_loop_boolean_dict
        else:
            logger.info(f".rod file parsing warning: Not all rod-keys were parsed.")
            return cif_key_loop_boolean_dict

    def key_pos_after_loop(self, loop_pos_lists, key_pos_list):
        loop_key_positions = []
        for loop_pos_list in loop_pos_lists:
            counter = 1
            while loop_pos_list + counter in key_pos_list:
                if (
                    counter >= 100
                ):  # implemented to avoid infinite loop, how to do better?
                    raise IndexError
                loop_key_positions.append(loop_pos_list + counter)
                counter += 1

        return loop_key_positions

    def get_cif_value_from_key(
        self, value_key: str, is_cif_loop_value=False
    ) -> str | list:
        """
        Parse the top-level Prodigy export settings into a dict.

        Parameters
        ----------
        value_key : str
            name of the key value, which is used for extraction

        is_cif_loop_value : boolean
            if the key value, is part of a loop structure, this has to be set
            correctly to extract the respective array-like values

        Returns
        -------
        output_list : str, list or np.array
            Values, list, or np.array which is assigned to the respective key in the cif file

        """

        block = self.cif_block  # extract main block of cif file
        if not is_cif_loop_value:  # is single value via _key = value
            value = block.find_value(value_key)
            # perform processing if string is not single line value
            if value.count("\n") > 0:
                value = value.replace(";\n", "")
                value = value.replace("\n;", "")
                if value.count("\n") > 0:
                    value = value.replace("\n", " ")
                return value.lstrip()  # remove leading space if it is present
            if value.count("\n") == 0:
                if value.startswith("'"):
                    return value.replace("'", "")
                return value
        if is_cif_loop_value:  # if block like value via loop_ = [....]
            output_list = []
            for element in block.find_loop(value_key):
                output_list.append(element)
            # try: # try to convert to numpy array
            #    output_list = np.array(output_list, dtype=float)
            #    return output_list
            try:  # try to convert to numpy array
                output_list_float = [float(item) for item in output_list]
                return output_list_float
            except ValueError:  # default string output if not convertable to float
                return output_list
        return None

    def extract_keys_and_values_from_cif(self):
        loop_positions = self.get_string_position("loop_\n")
        key_pos_non_loop = self.get_string_position("_", check_only_pos_zero=True)
        key_pos_in_loops = self.key_pos_after_loop(loop_positions, key_pos_non_loop)
        cif_key_dict_with_loop_boolean = self.get_keys_and_loop_boolean(
            key_pos_non_loop, key_pos_in_loops
        )

        # create a dictionary, and extract all the values by using the keys in correct formatting
        cif_dict_key_value_pair_dict = {}
        for key in cif_key_dict_with_loop_boolean:
            bool_loop_value = cif_key_dict_with_loop_boolean[key]
            cif_dict_key_value_pair_dict[key] = self.get_cif_value_from_key(
                key, is_cif_loop_value=bool_loop_value
            )

        return cif_dict_key_value_pair_dict

    def _parse(self, file: Path, **kwargs) -> None:
        self.get_cif_file_content(file)
        cif_fields = self.extract_keys_and_values_from_cif()

        # the measured spectrum itself -> self.data; everything else -> self.attrs
        self.data = {
            key: cif_fields.pop(key)
            for key in ROD_SPECTRUM_DATA_KEYS
            if key in cif_fields
        }
        self.attrs = cif_fields

        # replace the [ and ] to avoid conflicts in processing with pynxtools NXclass assignments
        self.attrs = {
            key.replace("_[local]_", "_local_"): value
            for key, value in self.attrs.items()
        }

        self.unused_attrs = copy.deepcopy(self.attrs)

        self.attrs.update(build_citation_fields(self.attrs))
        for consumed_key in (
            "_publ_author_name",
            "_publ_section_title",
            "_journal_name_full",
            "_journal_volume",
            "_journal_page_first",
            "_journal_page_last",
            "_journal_year",
        ):
            self.unused_attrs.pop(consumed_key, None)

        if self.attrs.get("_cod_database_code") is not None or "":
            self.attrs["COD_service_name"] = "Crystallography Open Database"
            del self.unused_attrs["_cod_database_code"]

        if self.attrs.get("_cell_length_a") is not None or "":
            # transform 9.40(3) to 9.40
            length_a = re.sub(r"\(\d+\)", "", self.attrs.get("_cell_length_a"))
            length_b = re.sub(r"\(\d+\)", "", self.attrs.get("_cell_length_b"))
            length_c = re.sub(r"\(\d+\)", "", self.attrs.get("_cell_length_c"))
            self.attrs["rod_unit_cell_length_abc"] = [
                float(length_a),
                float(length_b),
                float(length_c),
            ]
            del self.unused_attrs["_cell_length_a"]
            del self.unused_attrs["_cell_length_b"]
            del self.unused_attrs["_cell_length_c"]
        if self.attrs.get("_cell_angle_alpha") is not None or "":
            # transform 9.40(3) to 9.40
            angle_alpha = re.sub(r"\(\d+\)", "", self.attrs.get("_cell_angle_alpha"))
            angle_beta = re.sub(r"\(\d+\)", "", self.attrs.get("_cell_angle_beta"))
            angle_gamma = re.sub(r"\(\d+\)", "", self.attrs.get("_cell_angle_gamma"))
            self.attrs["rod_unit_cell_angles_alphabetagamma"] = [
                float(angle_alpha),
                float(angle_beta),
                float(angle_gamma),
            ]
            del self.unused_attrs["_cell_angle_alpha"]
            del self.unused_attrs["_cell_angle_beta"]
            del self.unused_attrs["_cell_angle_gamma"]

        # This changes all uppercase string elements to lowercase string elements for the given key, within a given key value pair
        key_to_make_value_lower_case = "_raman_measurement.environment"
        environment_name_str = self.attrs.get(key_to_make_value_lower_case)
        if environment_name_str is not None:
            self.attrs[key_to_make_value_lower_case] = environment_name_str.lower()

        # transform the string into a datetime object
        time_key = "_raman_measurement.datetime_initiated"
        date_time_str = self.attrs.get(time_key)
        if date_time_str is not None:
            date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")
            # assume UTC for .rod data, as this is not specified in detail
            tzinfo = datetime.timezone.utc
            if isinstance(date_time_obj, datetime.datetime):
                if tzinfo is not None:
                    # Apply the specified timezone to the datetime object
                    date_time_obj = date_time_obj.replace(tzinfo=tzinfo)

                # assign the dictionary the corrected date format
                self.attrs[time_key] = date_time_obj.isoformat()

        # remove capitalization
        objective_type_key = "_raman_measurement_device.optics_type"
        objective_type_str = self.attrs.get(objective_type_key)
        if objective_type_str is not None:
            self.attrs[objective_type_key] = objective_type_str.lower()
            # set a valid raman NXDL value, but only if it matches one of the correct ones:
            objective_type_list = ["objective", "lens", "glass fiber", "none"]
            if self.attrs.get(objective_type_key) not in objective_type_list:
                self.attrs[objective_type_key] = "other"

    def post_process(self, eln_data: dict[str, Any]) -> None:
        wavelength_nm = float(
            self.attrs.get("_raman_measurement_device.excitation_laser_wavelength")
        )
        resolution_inverse_cm = float(
            self.attrs.get("_raman_measurement_device.resolution")
        )

        if wavelength_nm is not None and resolution_inverse_cm is not None:
            # assume the resolution is referred to the resolution at the laser wavelength
            wavelength_inverse_cm = 1e7 / wavelength_nm
            resolution_nm = (
                resolution_inverse_cm / wavelength_inverse_cm * wavelength_nm
            )

            # update the data dictionary
            self.attrs[
                "/ENTRY[entry]/INSTRUMENT[instrument]/wavelength_resolution/physical_quantity"
            ] = "wavelength"
            self.attrs[
                "/ENTRY[entry]/INSTRUMENT[instrument]/wavelength_resolution/resolution"
            ] = resolution_nm
            self.attrs[
                "/ENTRY[entry]/INSTRUMENT[instrument]/wavelength_resolution/resolution/@units"
            ] = "nm"
            # remove this key from original input data
            del self.unused_attrs["_raman_measurement_device.resolution"]

        diffraction_grating = self.attrs.get(
            "_raman_measurement_device.diffraction_grating"
        )

        if diffraction_grating is not None:
            self.attrs[
                "/ENTRY[entry]/INSTRUMENT[instrument]/MONOCHROMATOR[monochromator]/GRATING[grating]/period"
            ] = 1 / float(diffraction_grating)


def _strip_cif_quotes(value: str) -> str:
    return value.strip().strip("'").strip('"')


def _join_authors(author_names: str | list | None) -> str | None:
    if not author_names:
        return None
    if isinstance(author_names, str):
        author_names = [author_names]
    cleaned = [_strip_cif_quotes(name) for name in author_names if name]
    return "; ".join(cleaned) if cleaned else None


def build_citation_fields(raman_data: dict) -> dict[str, Any]:
    """
    Build the two NXcite ("citeID") instances for a parsed .rod entry:

    - citeID[cite_publication]: the original paper reporting this Raman spectrum,
      built from the publication keys present in the .rod file.
    - citeID[cite_rod]: the ROD record itself, including ROD's own citation
      request and license (CC0 1.0), so the NeXus file is self-describing even
      outside NOMAD.

    Returns a dict of synthetic keys to be merged into the parsed .rod data and
    referenced from config_file_rod.json via "@attrs:<key>".
    """
    citation_fields: dict[str, Any] = {}

    author = _join_authors(raman_data.get("_publ_author_name"))
    title = raman_data.get("_publ_section_title")
    journal = raman_data.get("_journal_name_full")
    volume = raman_data.get("_journal_volume")
    page_first = raman_data.get("_journal_page_first")
    page_last = raman_data.get("_journal_page_last")
    year = raman_data.get("_journal_year")
    doi = raman_data.get("_journal_paper_doi")

    if author is not None:
        citation_fields["rod_citation_publication_author"] = author

    if title or doi:
        pages = (
            f"{page_first}-{page_last}"
            if page_first and page_last
            else (page_first or page_last or "")
        )
        description = ". ".join(part for part in (title, journal) if part)
        tail = ", ".join(part for part in (volume, pages) if part)
        if tail:
            description += f", {tail}"
        if year:
            description += f" ({year})"
        if description:
            citation_fields["rod_citation_publication_description"] = f"{description}."

    rod_code = raman_data.get("_rod_database.code")
    if rod_code is not None:
        citation_fields["rod_citation_rod_url"] = ROD_RECORD_URL_TEMPLATE.format(
            code=rod_code
        )
        citation_fields["rod_citation_rod_description"] = (
            f"Entry {rod_code} in the Raman Open Database (ROD). "
            f"{ROD_LICENSE_TEXT} Please also cite the database: {ROD_CITATION_TEXT}"
        )

    return citation_fields
