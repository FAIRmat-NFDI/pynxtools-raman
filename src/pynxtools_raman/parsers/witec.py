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
from pathlib import Path
from typing import Any

import numpy as np

from pynxtools_raman.parsers.base import _RamanParser

__all__ = ["WitecParser"]

# WITec's own DataUnit strings aren't always valid unit strings on their own
# (e.g. a CCD detector's counts are exported as "CCD cts", not "counts").
# Only entries actually observed in exported files should be added here.
_WITEC_ALIASES = {
    "DataUnit": ("CCD cts", "counts"),
}


class WitecParser(_RamanParser):
    """
    Parses .txt exports from WITec Alpha Raman spectrometers: the [Data]
    section into the measured x/y arrays (self.data), and the [Header]
    section into scalar instrument metadata (self.attrs).
    """

    supported_file_extensions = (".txt",)
    config_file = "config_file_witec.json"
    unused_attrs_group_name = "unused_witec_keys"

    def matches_file(self, file: Path) -> bool:
        """A WITec Alpha .txt export declares both a [Header] and a [Data]
        section near the top of the file."""
        try:
            with open(file, encoding="utf-8") as witec_file:
                head = "".join(line for _, line in zip(range(50), witec_file))
        except OSError:
            return False
        return "[Header]" in head and "[Data]" in head

    def _parse(self, file: Path, **kwargs) -> None:
        with open(file) as witec_file:
            lines = witec_file.readlines()

        header_dict: dict[str, str] = {}
        data: list[list[float]] = []
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
                # The header is set exactly until the float-like column data starts
                if line_count > data_mini_header_length:
                    values = line.split(",")
                    data.append([float(values[0].strip()), float(values[1].strip())])

        # Transform: [[A, B], [C, D], [E, F]] into [[A, C, E], [B, D, F]]
        transposed = [list(item) for item in zip(*data)]

        self.data = {"data/x_values": transposed[0], "data/y_values": transposed[1]}

        # Convert values to a normalized representation.
        for key, (old, new) in _WITEC_ALIASES.items():
            if header_dict.get(key) == old:
                header_dict[key] = new

        # [Header] fields (e.g. XAxisUnit, DataUnit, PositionX, ...) are scalar
        # metadata about the measurement, not the measurement itself.
        self.attrs = dict(header_dict)
        self.unused_attrs = dict(header_dict)

    def post_process(self, eln_data: dict[str, Any]) -> None:
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
            wavelength_keys = [key for key in eln_data if substring in key]
            # Filter the matching keys for the strings, which contain this substring at the end only
            filtered_list = [
                string for string in wavelength_keys if string.endswith(substring)
            ]
            # get the laser wavelength
            laser_wavelength = eln_data.get(filtered_list[0])
            return laser_wavelength

        laser_wavelength = get_incident_wavelength_from_NXraman()

        x_values_raman = transform_nm_to_wavenumber(
            laser_wavelength, self.data["data/x_values"]
        )

        # update the data dictionary
        self.data["data/x_values_raman"] = x_values_raman
