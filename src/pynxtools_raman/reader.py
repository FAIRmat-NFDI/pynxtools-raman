from typing import Any, Tuple
from typing import Dict

import math
import os
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Tuple

import numpy as np
import pandas as pd
import yaml
from pynxtools import get_nexus_version, get_nexus_version_hash
from pynxtools.dataconverter.helpers import extract_atom_types
from pynxtools.dataconverter.readers.base.reader import BaseReader
from pynxtools.dataconverter.readers.utils import FlattenSettings, flatten_and_replace


from pynxtools.dataconverter.readers.base.reader import BaseReader

# Still hardcoded parameters:
# "spectrum_data_x" <- name of X data array
# "spectrum_data_x_Raman" <- name of generated X data array in Raman reference frame
# "spectrum_data_y" <- Name of y data array
# "filename"

DEFAULT_HEADER = {"sep": "\t", "skip": 0}


CONVERT_DICT = {
    "unit": "@units",
    "detector": "detector_TYPE[detector_DU970BV]",  # "detector": "detector_TYPE[detector_DU970BV]", sollte auch passen mit "detector": "DETECTOR[detector_DU970BV]",
    "source_532nmlaser": "SOURCE[source_532nmlaser]",
    "beam_532nmlaser": "beam_TYPE[beam_532nmlaser]",
    "incident_beam": "beam_incident",  # this entry can be removed from NXraman definition, as at least one beam was made required in NXopt after the workshop
    "Data": "DATA[data]",
    "instrument": "INSTRUMENT[instrument]",
    "sample": "SAMPLE[sample_PET_or_PS]",
    "user": "USER[user]",
    "spectrum_data_y": "DATA[data]/spectrum_data_y",
    "spectrum_data_x": "DATA[data]/spectrum_data_x",
    "spectrum_data_y_unit": "DATA[data]/spectrum_data_y/@units",
    "spectrum_data_x_unit": "DATA[data]/spectrum_data_x/@units",
    "spectrum_data_y_longname": "DATA[data]/spectrum_data_y/@long_name",
    "spectrum_data_x_longname": "DATA[data]/spectrum_data_x/@long_name",
    "source_type": "type",
    "device_information": "FABRICATION[device_information]",
    "monochromator": "MONOCHROMATOR[monochromator]",
    "objective_lens": "LENS_OPT[objective_lens]",
}

CONFIG_KEYS = [
    "colnames",
    "filename",
    "filename_image1",
    "filename_image2",
    "filename_reference",
    "plot_name_y",
    "plot_name_x",
    "sep",
    "skip",
    "unit_y",
    "unit_x",
]

REPLACE_NESTED: Dict[str, str] = {}
# REPLACE_NESTED = {
#    #    "instrument": "INSTRUMENT[instrument]",
# }


def load_header(filename, default):
    """load the yaml description file, and apply defaults from
    the defalut dict for all keys not found from the file.
    Parameters:
        filename:           a yaml file containing the definitions
        default_header:     predefined default values
    Returns:
        a dict containing the loaded information
    """

    with open(filename, "rt", encoding="utf8") as file:
        header = yaml.safe_load(file)

    clean_header = header

    for key, value in default.items():
        if key not in clean_header:
            clean_header[key] = value

    if "sep" in header:
        clean_header["sep"] = header["sep"].encode("utf-8").decode("unicode_escape")

    return clean_header


def load_as_pandas_array(my_file, header):
    """Load a CSV output file using the header dict.
    Use the fields: colnames, skip and sep from the header
    to instruct the csv reader about:
    colnames    -- column names
    skip        -- how many lines to skip
    sep         -- separator character in the file
    Parameters:
        my_file  string, file name
        header   dict header read from a yaml file
    Returns:
        A pandas array is returned.
    """
    required_parameters = ("colnames", "skip", "sep")
    for required_parameter in required_parameters:
        if required_parameter not in header:
            raise ValueError("colnames, skip and sep are required header parameters!")

    if not os.path.isfile(my_file):
        raise IOError(f"File not found error: {my_file}")

    whole_data = pd.read_csv(
        my_file,
        # use header = None and names to define custom column names
        header=None,
        encoding="latin",
        names=header["colnames"],
        skiprows=header["skip"],
        delimiter=header["sep"],
    )
    return whole_data


def populate_header_dict(file_paths):
    """This function creates and populates the header dictionary
    reading one or more yaml file.
    Parameters:
        file_paths  a list of file paths to be read
    Returns:
        a dict merging the content of all files
    """

    header = DEFAULT_HEADER

    for file_path in file_paths:
        if os.path.splitext(file_path)[1].lower() in [".yaml", ".yml"]:
            header = load_header(file_path, header)
            if "filename" not in header:
                raise KeyError("filename is missing from", file_path)
            data_file = os.path.join(os.path.split(file_path)[0], header["filename"])

            # if the path is not right, try the path provided directly
            if not os.path.isfile(data_file):
                data_file = header["filename"]

    return header, data_file


def populate_template_dict(header, template):
    """The template dictionary is then populated according to the content of header dictionary."""

    eln_data_dict = flatten_and_replace(
        FlattenSettings(
            dic=header,
            convert_dict=CONVERT_DICT,
            replace_nested=REPLACE_NESTED,
            ignore_keys=CONFIG_KEYS,
        )
    )

    template.update(eln_data_dict)

    return template


def header_labels(header):
    """Define data labels (column names)"""

    labels = {"CCD_cts": []}
    for key, val in labels.items():
        val.append(f"{key}")
    return labels


def data_array(whole_data, data_index):
    """User defined variables to produce slices of the whole data set"""

    axis_label = whole_data.keys()[data_index]

    length_data_entries = len(whole_data[axis_label])
    my_data_array = np.empty([length_data_entries])

    my_data_array[:] = whole_data[axis_label].to_numpy().astype("float64")

    return my_data_array


class RamanReader(BaseReader):
    """
    Reader for my method....
    PLEASE UPDATE
    """

    supported_nxdls = ["NXraman"]

    @staticmethod
    def populate_header_dict_with_datasets(file_paths):
        """This is a raman-specific processing of data.
        The procedure is the following:
        - the header dictionary is initialized reading a yaml file
        - the data are read from header["filename"] and saved in a pandas object
        - an array is shaped according to application definition in a 5D array (numpy array)
        - the array is saved in a HDF5 file as a dataset
        - virtual datasets instances are created in the header dictionary,
        referencing to data in the created HDF5 file.
        - the header is finally returned, ready to be parsed in the final template dictionary
        """
        header, data_file = populate_header_dict(file_paths)

        if os.path.isfile(data_file):
            whole_data = load_as_pandas_array(data_file, header)
        else:
            # this we have tried, we should throw an error...
            whole_data = load_as_pandas_array(header["filename"], header)

        # As the specific name of beam entries in unknown, extract all beam names from instrument level
        list_of_beams = []
        for i in header["instrument"].keys():
            # look for all entries in instrument, add only if the first letters are like "beam_"
            if len(i) > 4:
                if i[:5] == "beam_":
                    list_of_beams.append(i)
        light_source_name = list_of_beams[0]
        laser_wavelength = header["instrument"][light_source_name][
            "incident_wavelength"
        ]["value"]

        def transform_nm_to_wavenumber(lambda_laser, lambda_measurement):
            return -(1e7 / lambda_measurement - 1e7 / lambda_laser)

        measured_wavelengths = whole_data["wavelength"].to_numpy()

        # Add the new created data to the panda data frame
        data_x_Raman = transform_nm_to_wavenumber(
            laser_wavelength * np.ones(len(measured_wavelengths)), measured_wavelengths
        )
        whole_data["DATA[data]/spectrum_data_x_Raman"] = data_x_Raman

        labels = header_labels(header)

        def add_data_to_header(data_set, data_column_index, name):
            header[str(name)] = data_array(data_set, data_column_index)

        # add specific data parts to the header of the file
        add_data_to_header(whole_data, 0, "spectrum_data_x")
        add_data_to_header(whole_data, 1, "spectrum_data_y")
        add_data_to_header(whole_data, 2, "DATA[data]/spectrum_data_x_Raman")

        if "atom_types" not in header["sample"]:
            header["atom_types"] = extract_atom_types(
                header["sample"]["chemical_formula"]
            )

        return header, labels

    def read(
        self,
        template: dict = None,
        file_paths: Tuple[str] = None,
        objects: Tuple[Any] = None,
    ) -> dict:
        """Reads data from given file and returns a filled template dictionary.
        A handlings of virtual datasets is implemented:
        virtual dataset are created inside the final NeXus file.
        The template entry is filled with a dictionary containing the following keys:
        - link: the path of the external data file and the path of desired dataset inside it
        - shape: numpy array slice object (according to array slice notation)
        """

        if not file_paths:
            raise IOError("No input files were given to raman Reader.")

        # The header dictionary is filled with entries.
        header, labels = RamanReader.populate_header_dict_with_datasets(file_paths)
        # The template dictionary is filled
        template = populate_template_dict(header, template)

        # assign main axis for data entry
        template[f"/ENTRY[entry]/DATA[data]/@signal"] = f"spectrum_data_y"
        template[f"/ENTRY[entry]/DATA[data]/@axes"] = f"spectrum_data_x_Raman"

        # add unit and long name for calculated Raman data
        template[f"/ENTRY[entry]/DATA[data]/spectrum_data_x_Raman/@units"] = "1/cm"
        template[f"/ENTRY[entry]/DATA[data]/spectrum_data_x_Raman/@long_name"] = (
            f"Raman Shift"
        )

        return template


# This has to be set to allow the convert script to use this reader. Set it to "MyDataReader".
READER = RamanReader

# pynxtools will call:
# data = data_reader().read(template=Template(template), file_paths=input_file, **kwargs)
