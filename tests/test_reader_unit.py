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
"""Direct unit tests for RamanReader's @attrs:/@data: split and file-format
guard behavior, as opposed to tests/test_reader.py's end-to-end conversion test.
"""

from pathlib import Path

import pytest

from pynxtools_raman.reader import RamanReader

ROD_FIXTURE = Path(__file__).parent / "data" / "rod" / "rod_file_1000679.rod"
WITEC_FIXTURE = (
    Path(__file__).parent / "data" / "witec" / "Si-wafer-Raman-Spectrum-1.txt"
)


class TestGetAttr:
    def test_resolves_from_attrs_and_consumes_missing_meta_data(self):
        reader = RamanReader()
        reader.attrs = {"foo": "1.5"}
        reader.missing_meta_data = {"foo": "1.5"}

        value = reader.get_attr("/ENTRY[entry]/SAMPLE[sample]/foo", "foo")

        assert value == pytest.approx(1.5)
        assert "foo" not in reader.missing_meta_data

    def test_space_group_under_sample_stays_a_string(self):
        reader = RamanReader()
        reader.attrs = {"_space_group_IT_number": "62"}
        reader.missing_meta_data = {}

        value = reader.get_attr(
            "/ENTRY[entry]/SAMPLE[sample]/space_group", "_space_group_IT_number"
        )

        assert value == "62"

    def test_missing_key_returns_none_and_warns(self, caplog):
        reader = RamanReader()
        reader.attrs = {}
        reader.missing_meta_data = {}

        value = reader.get_attr("/ENTRY[entry]/SAMPLE[sample]/foo", "foo")

        assert value is None
        assert "No axis name corresponding to the path foo" in caplog.text


class TestGetData:
    def test_resolves_from_data(self):
        reader = RamanReader()
        reader.data = {"data/x_values": [1.0, 2.0]}

        value = reader.get_data(
            "/ENTRY[entry]/DATA[data]/AXISNAME[x_values]", "data/x_values"
        )

        assert value == [1.0, 2.0]

    def test_does_not_touch_missing_meta_data(self):
        reader = RamanReader()
        reader.data = {"data/x_values": [1.0]}
        reader.missing_meta_data = {"data/x_values": "unrelated attrs entry"}

        reader.get_data("/ENTRY[entry]/DATA[data]/AXISNAME[x_values]", "data/x_values")

        # get_data must never consume missing_meta_data - only get_attr does.
        assert "data/x_values" in reader.missing_meta_data


class TestHandleFileSkipsOnMismatch:
    def test_handle_rod_file_skips_a_non_matching_file(self, tmp_path):
        bogus = tmp_path / "not_a_rod_file.rod"
        bogus.write_text("this is not a CIF file\n")
        reader = RamanReader()

        result = reader.handle_rod_file(str(bogus))

        assert result == {}
        assert reader._active_parser is None
        assert reader.attrs == {}

    def test_handle_txt_file_skips_a_non_matching_file(self, tmp_path):
        bogus = tmp_path / "not_a_witec_file.txt"
        bogus.write_text("just some random text\n")
        reader = RamanReader()

        result = reader.handle_txt_file(str(bogus))

        assert result == {}
        assert reader._active_parser is None
        assert reader.attrs == {}

    def test_handle_rod_file_parses_a_matching_file(self):
        reader = RamanReader()

        result = reader.handle_rod_file(str(ROD_FIXTURE))

        assert result == {}
        assert reader._active_parser is not None
        assert reader.attrs

    def test_handle_txt_file_parses_a_matching_file(self):
        reader = RamanReader()

        result = reader.handle_txt_file(str(WITEC_FIXTURE))

        assert result == {}
        assert reader._active_parser is not None
        assert reader.data
