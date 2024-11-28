import logging

from typing import Dict, Any

logger = logging.getLogger("pynxtools")

def get_data(self, key: str, path: str) -> Any:
    """Returns measurement data from the given eln_data entry."""
    if path.endswith(("x_values", "y_values","x_values_raman")):
        return self.txt_data.get(f"data/{path}")
    else:
        logger.warning(f"No axis name corresponding to the path {path}.")