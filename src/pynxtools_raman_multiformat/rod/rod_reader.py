


import copy
from pynxtools_raman_multiformat.reader_utils import (
    RamanMapper,
    _check_valid_value,
    _re_map_single_value,
#    construct_data_key,
    construct_entry_name,
)

from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from pynxtools_raman_multiformat.rod.rod_data_model import RodHeader#, ScientaRegion

import pynxtools_raman_multiformat.reader_rod_utils as pynx_rod

class MapperRod(RamanMapper):
    """
    Class for restructuring data from
    Raman Open Database files into a structured python
    dictionaries.
    """

    config_file = "config_rod.json"

    def _select_parser(self):
        """
        Select Raman Open Database parser based on the file extension.

        Returns
        -------
        ScientaParser
            Parser for reading .txt or .ibw files exported by Scienta.

        """
        if str(self.file).endswith(".txt"):
            return RodTxtParser()
        elif str(self.file).endswith(".rod"):
            return RodParser()
        raise ValueError(MapperRod.__file_err_msg__)

    def construct_data(self):
        """Map Parser data to NXmpes-ready dict."""
        # pylint: disable=duplicate-code
        spectra = copy.deepcopy(self.raw_data)

        # yay, I see some data...
        print(self.raw_data,"#raw data")

        self._raman_dict["data"]: dict = {}

        template_key_map = {
            "file_info": ["data_file", "sequence_file"],
            "user": [
                "user_name",
            ],
            "instrument": [
                "instrument_name",
                "vendor",
            ],
            "source_xray": [],
            "beam_xray": [
                "excitation_energy",
            ],
            "electronanalyser": [],
            "collectioncolumn": [
                "lens_mode",
            ],
            "energydispersion": [
                "acquisition_mode",
                "pass_energy",
            ],
            "detector": [
                "detector_first_x_channel",
                "detector_first_y_channel",
                "detector_last_x_channel",
                "detector_last_y_channel",
                "detector_mode",
                "dwell_time",
                "time_per_spectrum_channel",
            ],
            "manipulator": [
                "manipulator_r1",
                "manipulator_r2",
            ],
            "calibration": [],
            "sample": ["sample_name"],
            "region": [
                "center_energy",
                "energy_axis",
                "energy_scale",
                "energy_scale_2",
                "energy_size",
                "no_of_scans",
                "region_id",
                "spectrum_comment",
                "start_energy",
                "step_size",
                "stop_energy",
                "time_stamp",
                "intensity/@units",
            ],
            # 'unused': [
            #     'energy_unit',
            #     'number_of_slices',
            #     'software_version',
            #     'spectrum_comment',
            #     'start_date',
            #     'start_time',
            #     'time_per_spectrum_channel'
            # ]
        }

        for spectrum in spectra:
            self._update_raman_dict_with_spectrum(spectrum, template_key_map)





class RodParser:
    """Parser for Scienta TXT exports."""

    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.lines: List[str] = []
        self.header = RodHeader()
        self.spectra: List[Dict[str, Any]] = []

    def parse_file(self, file: Union[str, Path], **kwargs):
        """
        Parse the file's data and metadata into a flat
        list of dictionaries.


        Parameters
        ----------
        file : str
            Filepath of the TXT file to be read.

        Returns
        -------
        self.spectra
            Flat list of dictionaries containing one spectrum each.

        """
        print(file)
        rod = pynx_rod.RodReader()
        # read the rod file
        rod.get_cif_file_content(file)
        # get the key and value pairs from the rod file
        self.raman_data = rod.extract_keys_and_values_from_cif()

        #self._read_lines(file)
        #self._parse_header() # no header present yet

        #for region_id in range(1, self.header.no_of_regions + 1):
        #    self._parse_region(region_id)

        return self.raman_data

    def _read_lines(self, file: Union[str, Path]):
        """
        Read all lines from the input txt files.


        Parameters
        ----------
        file : str
            Filepath of the TXT file to be read.

        Returns
        -------
        None.

        """
        with open(file, encoding="utf-8") as txt_file:
            for line in txt_file:
                self.lines += [line]












class RodTxtParser:
    """Parser for Raman Open Database txt files """
    # This is just a placeholder in for development

    def __init__(self):
        self.lines: List[str] = []
        self.header = RodHeader()
        self.spectra: List[Dict[str, Any]] = []

class RodParser_OLD:
    """Parser for Raman Open Database .rod files """

    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.lines: List[str] = []
        self.spectra: List[Dict[str, Any]] = []

    def parse_file(self, file: Union[str, Path], **kwargs):
        """
        Reads the igor binarywave files and returns a list of
        dictionary containing the wave data.

        Parameters
        ----------
        file : str
            Filepath of the TXT file to be read.

        Returns
        -------
        self.spectra
            Flat list of dictionaries containing one spectrum each.

        """
        #ibw = binarywave.load(file)
        #ibw_version, wave = ibw["version"], ibw["wave"]

        #notes = self._parse_note(wave["note"])

        #data_unit_label, data_unit = self._parse_unit(wave["data_units"])
        #dimension_unit_label, dimension_unit = self._parse_unit(wave["dimension_units"])

        #wave_header = wave["wave_header"]
        #data = wave["wData"]


        # Initiate rod reader as calss
        rod = pynx_rod.RodReader()
        # read the rod file
        rod.get_cif_file_content(file)
        # get the key and value pairs from the rod file
        self.raman_data = rod.extract_keys_and_values_from_cif()


        #self.spectra = 





        # Not needed at the moment.
        # TODO: Add support for formulas if they are written by the
        # measurement software.
        # formula = wave["formula"]
        # labels = wave["labels"]
        # spectrum_indices = wave["sIndices"]
        # bin_header = wave["bin_header"]
        if False:
            if len(data.shape) == 1:
                self.no_of_regions = 1
            else:
                self.no_of_regions = data.shape[0]

            for region_id in range(0, self.no_of_regions):
                region = ScientaRegion(region_id=region_id)
                region_fields = list(region.__dataclass_fields__.keys())
                overwritten_fields = ["region_id", "time_stamp", "data"]
                unused_notes_keys = []

                for key, note in notes.items():
                    if _check_valid_value(note):
                        if key in region_fields:
                            setattr(region, key, note)
                            overwritten_fields += [key]
                        else:
                            unused_notes_keys += [key]

                energies = self.axis_for_dim(wave_header, dim=region_id)
                axs_unit = self.axis_units_for_dim(wave_header, dim=region_id)

                if data.ndim == 1:
                    intensities = data
                else:
                    intensities = data[region_id]

                # Convert date and time to ISO8601 date time.
                region.time_stamp = _construct_date_time(
                    region.start_date, region.start_time
                )

                region.energy_size = len(energies)
                region.energy_axis = energies

                region.data = {
                    "energy": np.array(energies),
                    "intensity": np.array(intensities),
                }

                region.validate_types()

                spectrum_dict = region.dict()

                for key in unused_notes_keys:
                    spectrum_dict[key] = notes[key]

                spectrum_dict["igor_binary_wave_format_version"] = ibw_version
                spectrum_dict["intensity/@units"] = convert_units(data_unit_label)

                self.spectra.append(spectrum_dict)

            return self.spectra