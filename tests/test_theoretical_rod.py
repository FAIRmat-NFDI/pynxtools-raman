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
"""A .rod file with a theoretical spectrum is skipped with a warning."""

from pathlib import Path

import pytest

from pynxtools_raman.reader import RamanReader

ROD_FIXTURE = Path(__file__).parent / "data" / "rod" / "rod_file_1000679.rod"


@pytest.fixture
def theoretical_rod(tmp_path):
    """The ROD fixture, with the measured spectrum renamed to a theoretical one."""
    text = ROD_FIXTURE.read_text()
    text = text.replace(
        "_raman_spectrum.raman_shift", "_raman_theoretical_spectrum.frequency"
    )
    text = text.replace(
        "_raman_spectrum.intensity", "_raman_theoretical_spectrum.intensity"
    )
    file = tmp_path / "theoretical.rod"
    file.write_text(text)
    return file


def test_theoretical_rod_leaves_config_file_alone(theoretical_rod):
    reader = RamanReader()

    reader.handle_rod_file(str(theoretical_rod))

    assert reader.config_file is None
    assert reader._active_parser is None


def test_theoretical_rod_is_skipped_without_error(theoretical_rod, caplog):
    reader = RamanReader()

    output = reader.read(file_paths=(str(theoretical_rod),))

    assert "Theoretical Raman data .rod file found" in caplog.text
    assert dict(output) == {"/@default": "entry"}
