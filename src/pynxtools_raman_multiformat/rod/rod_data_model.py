
"""
Data model for data from Raman Open Database File.
"""


from dataclasses import dataclass, field
import numpy as np

from pynxtools_raman_multiformat.reader_utils import RamanDataclass


@dataclass
class RodHeader(RamanDataclass):
    no_of_regions: int = 0
    software_version: str = ""
