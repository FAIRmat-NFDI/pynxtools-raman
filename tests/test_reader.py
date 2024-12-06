"""
Basic example based test for the stm reader
"""

import pytest
import os
from glob import glob
from pathlib import Path

from pynxtools.testing.nexus_conversion import ReaderTest


@pytest.mark.parametrize(
    "data_dir, caplog_level",
    [
        ("rod", "WARNING"),
        ("witec", "WARNING"),
    ],
)
def test_nexus_conversion(data_dir, caplog_level, tmp_path, caplog):
    """
    Tests the conversion into nexus.
    """
    caplog.clear()
    dir_path = Path(__file__).parent / f"data/{data_dir}"
    test = ReaderTest(
        nxdl="NXraman",
        reader_name="raman",
        files_or_dir=glob(os.path.join(dir_path, "*")),
        tmp_path=tmp_path,
        caplog=caplog,
    )
    test.convert_to_nexus(caplog_level=caplog_level, ignore_undocumented=False)
    test.check_reproducibility_of_nexus()
