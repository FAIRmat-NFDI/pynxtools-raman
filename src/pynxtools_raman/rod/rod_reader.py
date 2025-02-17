from typing import List, Dict, Any, Union
import gemmi  # for cif file handling

from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger("pynxtools")


class RodParser:
    """
    This class provides the ultilieies to read in a .rod file with "get_cif_file_content".
    Then extract all data via "extract_keys_and_values_from_cif" into a dictionary.
    """

    def __init__(self, *args, **kwargs):
        self.cif_doc = None
        self.cif_block = None
        self.lines = []

    def _read_lines(self, file: Union[str, Path]):
        """
        Read all lines from the input files.
        """
        with open(file, encoding="utf-8") as utf8_file:
            lines = utf8_file.readlines()

        return lines

    def get_cif_file_content(self, file_path):
        doc = gemmi.cif.read_file(file_path)
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
                logger.info(f"Problem during reading .rod file. 'rod_line' is None.")
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
                # Extract only the key, as this is always avaialble.
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
        loop_key_positons = []
        for loop_pos_list in loop_pos_lists:
            counter = 1
            while loop_pos_list + counter in key_pos_list:
                if (
                    counter >= 100
                ):  # implemented to avoid infinite loop, how to do better?
                    raise IndexError
                loop_key_positons.append(loop_pos_list + counter)
                counter += 1

        return loop_key_positons

    def get_cif_value_from_key(
        self, value_key: str, is_cif_loop_value=False
    ) -> Union[str, list]:
        """
        Parse the top-level Prodigy export settings into a dict.

        Parameters
        ----------
        value_key : str
            name of the key value, which is used for extraction

        is_cif_loop_value : boolean
            if the key value, is part of a loop structure, this has to be set
            correctly to extracat the respective array-like values

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
            # try: # try to conver tto numpy array
            #    output_list = np.array(output_list, dtype=float)
            #    return output_list
            try:  # try to conver tto numpy array
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


def post_process_rod(self) -> None:
    wavelength_nm = float(
        self.raman_data.get("_raman_measurement_device.excitation_laser_wavelength")
    )
    resolution_invers_cm = float(
        self.raman_data.get("_raman_measurement_device.resolution")
    )

    if wavelength_nm is not None and resolution_invers_cm is not None:
        # assume the resolution is referd to the resolution at the laser wavelength
        wavelength_invers_cm = 1e7 / wavelength_nm
        resolution_nm = resolution_invers_cm / wavelength_invers_cm * wavelength_nm

        # update the data dictionary
        self.raman_data[
            "/ENTRY[entry]/INSTRUMENT[instrument]/RESOLUTION[wavelength_resolution]/physical_quantity"
        ] = "wavelength"
        self.raman_data[
            "/ENTRY[entry]/INSTRUMENT[instrument]/RESOLUTION[wavelength_resolution]/resolution"
        ] = resolution_nm
        self.raman_data[
            "/ENTRY[entry]/INSTRUMENT[instrument]/RESOLUTION[wavelength_resolution]/resolution/@units"
        ] = "nm"
        # remove this key from original input data
        del self.missing_meta_data["_raman_measurement_device.resolution"]
