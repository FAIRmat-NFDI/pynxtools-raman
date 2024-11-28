import logging

from typing import Dict, Any

logger = logging.getLogger("pynxtools")

def get_data(self, key: str, path: str) -> Any:
    """
    Returns the data from a .rod file (Raman Open Database), which was trasnferred into a dictionary.
    """
    try:
        return float(self.rod_data.get(path))
    except:
        return self.rod_data.get(path)