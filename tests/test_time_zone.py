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
"""ROD dates have no time or time zone, so none must be invented."""

import logging
from pathlib import Path

from pynxtools.dataconverter.template import Template

from pynxtools_raman.reader import RamanReader

ROD_FILE = Path(__file__).parent / "data" / "rod" / "rod_file_1000679.rod"
START_TIME = "/ENTRY[entry]/start_time"


def _read(*files):
    return RamanReader().read(
        template=Template(), file_paths=tuple(str(f) for f in files)
    )


def test_rod_date_is_written_as_it_is(caplog):
    """The file says 2011-09-07, so no midnight and no UTC are added."""
    with caplog.at_level(logging.WARNING):
        template = _read(ROD_FILE)

    assert template[START_TIME] == "2011-09-07"
    assert "has no time or time zone" in caplog.text


def test_eln_start_time_wins_over_the_rod_date(tmp_path, caplog):
    """A full start time from the ELN is used, and nothing is warned."""
    eln = tmp_path / "eln_data.yaml"
    eln.write_text("start_time: '2011-09-07T14:30:00+02:00'\n")

    with caplog.at_level(logging.WARNING):
        template = _read(ROD_FILE, eln)

    assert template[START_TIME] == "2011-09-07T14:30:00+02:00"
    assert "has no time or time zone" not in caplog.text
