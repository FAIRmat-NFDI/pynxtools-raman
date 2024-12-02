import logging

from typing import Dict, Any

logger = logging.getLogger("pynxtools")

def get_data(self, key: str, path: str) -> Any:
    """
    Returns the data from a .rod file (Raman Open Database), which was trasnferred into a dictionary.
    """

    try:
        return float(self.raman_data.get(path))
    except:
        return self.raman_data.get(path)


def get_attr(self, key: str, path: str) -> Any:
    """
    Get the metadata that was stored in the main(=data) file.
    """
    return None

def post_process(self) -> None:
    """
    Post process the Raman data to add the Raman Shift from input laser wavelength and
    data wavelengths.
    """
    return {}
