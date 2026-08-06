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
"""Tests for the WITec Alpha (.txt) parser."""

from pathlib import Path

import pytest

from pynxtools_raman.parsers.witec import WitecParser

WITEC_FIXTURE = (
    Path(__file__).parents[1] / "data" / "witec" / "Si-wafer-Raman-Spectrum-1.txt"
)
ROD_FIXTURE = Path(__file__).parents[1] / "data" / "rod" / "rod_file_1000679.rod"


class TestWitecParserMatchesFile:
    def test_matches_real_witec_fixture(self):
        assert WitecParser.is_mainfile(WITEC_FIXTURE) is True

    def test_does_not_match_rod_fixture(self):
        assert WitecParser.is_mainfile(ROD_FIXTURE) is False

    def test_does_not_match_nonexistent_file(self, tmp_path):
        assert WitecParser.is_mainfile(tmp_path / "does_not_exist.txt") is False


class TestWitecParserParse:
    """WitecParser._parse against the real shipped fixture."""

    @pytest.fixture(scope="class")
    def parsed(self) -> WitecParser:
        parser = WitecParser()
        parser.parse(WITEC_FIXTURE)
        return parser

    def test_data_arrays_are_extracted(self, parsed):
        assert len(parsed.data["data/x_values"]) == len(parsed.data["data/y_values"])
        assert len(parsed.data["data/x_values"]) > 0
        assert all(isinstance(v, float) for v in parsed.data["data/x_values"][:5])

    def test_header_fields_land_in_attrs(self, parsed):
        assert parsed.attrs["XAxisUnit"] == "nm"
        assert parsed.attrs["PositionUnit"] == "µm"
        assert parsed.attrs["SizeX"] == "1"

    def test_data_unit_is_normalized(self, parsed):
        # The raw header value is "CCD cts", not a valid unit string on its own.
        assert parsed.attrs["DataUnit"] == "counts"

    def test_header_fields_start_out_unused(self, parsed):
        # Nothing has consumed them via the config file yet at this point.
        assert parsed.unused_attrs["PositionX"] == "2.3283064365387E-8"
        assert "data/x_values" not in parsed.unused_attrs


class TestWitecParserPostProcess:
    def test_zero_shift_when_measured_equals_laser_wavelength(self):
        parser = WitecParser()
        parser.data = {"data/x_values": [500.0]}

        parser.post_process(
            eln_data={"/ENTRY[entry]/instrument/beam_incident/wavelength": 500.0}
        )

        assert parser.data["data/x_values_raman"] == pytest.approx([0.0], abs=1e-9)

    def test_raman_shift_is_computed_from_wavelength(self):
        parser = WitecParser()
        parser.data = {"data/x_values": [550.0]}

        parser.post_process(
            eln_data={"/ENTRY[entry]/instrument/beam_incident/wavelength": 500.0}
        )

        expected = -(1e7 / 550.0 - 1e7 / 500.0)
        assert parser.data["data/x_values_raman"] == pytest.approx([expected])
