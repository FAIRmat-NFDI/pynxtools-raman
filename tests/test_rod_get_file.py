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
"""Tests for the low-level single-file ROD download (rod_get_file.py).

The `download` CLI command built on top of this now lives in rod_batch.py
(it shares its option surface with build-upload-batch); see
tests/test_rod_batch.py for CLI-level coverage.
"""

import requests

from pynxtools_raman.rod import rod_get_file


def test_save_rod_file_writes_into_output_dir(tmp_path, monkeypatch):
    class FakeResponse:
        text = "fake rod content"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(rod_get_file.requests, "post", lambda url: FakeResponse())

    path = rod_get_file.save_rod_file_from_ROD_via_API(1000679, output_dir=tmp_path)

    assert path == tmp_path / "1000679.rod"
    assert path.read_text(encoding="utf-8") == "fake rod content"


def test_save_rod_file_creates_output_dir_if_missing(tmp_path, monkeypatch):
    class FakeResponse:
        text = "fake rod content"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(rod_get_file.requests, "post", lambda url: FakeResponse())
    missing_dir = tmp_path / "nested" / "dir"

    path = rod_get_file.save_rod_file_from_ROD_via_API(1000679, output_dir=missing_dir)

    assert path == missing_dir / "1000679.rod"
    assert path.is_file()


def test_save_rod_file_returns_none_on_request_error(tmp_path, monkeypatch):
    def raise_connection_error(url):
        raise requests.exceptions.ConnectionError("no network")

    monkeypatch.setattr(rod_get_file.requests, "post", raise_connection_error)

    path = rod_get_file.save_rod_file_from_ROD_via_API(1000679, output_dir=tmp_path)

    assert path is None
