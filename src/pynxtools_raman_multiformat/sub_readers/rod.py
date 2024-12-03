import logging

from typing import Dict, Any

logger = logging.getLogger("pynxtools")


class MapperROD():
    def printing():
        print("Test")


def get_data_rod(self, key: str, path: str) -> Any:
    """
    Returns the data from a .rod file (Raman Open Database), which was trasnferred into a dictionary.
    """
    print(self.raman_data.get(path))
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