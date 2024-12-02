import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

logger = logging.getLogger("pynxtools")


#class SubReaderWitec():
#    def get_data(self, key: str, path: str) -> Any:
#        """Returns measurement data from the given eln_data entry."""
#        if path.endswith(("x_values", "y_values","x_values_raman")):
#            return self.raman_data.get(f"data/{path}")
#        else:
#            logger.warning(f"No axis name corresponding to the path {path}.")

def get_data(self, key: str, path: str) -> Any:
    """Returns measurement data from the given eln_data entry."""
    print("####",self.sub_reader_name)
    if path.endswith(("x_values", "y_values","x_values_raman")):
        return self.raman_data.get(f"data/{path}")
    else:
        logger.warning(f"No axis name corresponding to the path {path}.")

def get_attr(self, key: str, path: str) -> Any:
    """
    Get the metadata that was stored in the main(=data) file.
    """

    if self.txt_data is None:
        return None
    return self.txt_data.get(path)

def post_process_witec(self) -> None:
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
    x_values_raman = transform_nm_to_wavenumber(self, laser_wavelength, self.raman_data["data/x_values"])

    self.raman_data["data/x_values_raman"] = x_values_raman

