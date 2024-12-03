import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class RamanDataclass:
    """Generic class to hold a data model and a type validation method."""

    def validate_types(self):
        ret = True
        for field_name, field_def in self.__dataclass_fields__.items():
            actual_type = type(getattr(self, field_name))
            if actual_type != field_def.type:
                logger.warning(
                    f"Type mismatch in dataclass {type(self).__name__}. {field_name}: '{actual_type}' instead of '{field_def.type}'"
                )
                ret = False
        return ret

    def __post_init__(self):
        if not self.validate_types():
            raise ValueError(f"Type mismatch in dataclass {type(self).__name__}")

    def dict(self):
        return self.__dict__.copy()


class RamanMapper(ABC):
    """Abstract base class from mapping from a parser to NXmpes template"""

    def __init__(self):
        self.file: Union[str, Path] = ""
        self.raw_data: List[str] = []
        self._raman_dict: Dict[str, Any] = {}
        self._root_path = ""

        self.parser = None

    @abstractmethod
    def _select_parser(self):
        """
        Select the correct parser for the file extension and format.

        Should be implemented by the inheriting mapper.

        Returns
        -------
        Parser

        """

    @property
    def data_dict(self) -> dict:
        """Getter property."""
        return self._raman_dict

    def parse_file(self, file, **kwargs):
        """
        Parse the file using the Scienta TXT parser.

        """
        self.file = file

        self.parser = self._select_parser()
        self.raw_data = self.parser.parse_file(file, **kwargs)


        file_key = f"{self._root_path}/File"
        self._raman_dict[file_key] = file

        self.construct_data()

        return self.data_dict

    @abstractmethod
    def construct_data(self):
        """
        Map from individual parser format to NXmpes-ready dict.

        Should be implemented by the inheriting mapper.

        """


def construct_entry_name(parts: List[str]) -> str:
    """Construct name for the NXentry instances."""
    if len(parts) == 1:
        return align_name_part(parts[0])
    return "__".join([align_name_part(part) for part in parts])


def _re_map_single_value(
    input_key: str,
    value: Optional[Union[str, int, float, bool, np.ndarray]],
    map_functions: Dict[str, Any],
):
    """
    Map the values returned from the file to the preferred format for
    the parser output.

    """
    if isinstance(value, str) and value is not None:
        value = value.rstrip("\n")

    for key in map_functions:
        if key in input_key:
            map_method = map_functions[key]
            value = map_method(value)  # type: ignore[operator]
    return value



def _check_valid_value(value: Union[str, int, float, bool, np.ndarray]) -> bool:
    """
    Check if a string or an array is empty.

    Parameters
    ----------
    value : obj
        For testing, this can be a str or a np.ndarray.

    Returns
    -------
    bool
        True if the string or np.ndarray is not empty.

    """
    if isinstance(value, (str, int, float)) and value is not None:
        return True
    if isinstance(value, bool):
        return True
    if isinstance(value, np.ndarray) and value.size != 0:
        return True
    return False


def align_name_part(name_part: str):
    """Make one part of the entry name compliant with NeXus standards."""
    replacements = {
        " ": "_",
        ",": "",
        ".": "_",
        "-": "_",
        ":": "_",
    }

    for original, replacement in replacements.items():
        name_part = name_part.replace(original, replacement)

    return name_part
