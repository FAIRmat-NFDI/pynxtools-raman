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
"""Tests for the ROD batch-upload nomad.json metadata generator."""

import json

from pynxtools_raman.rod.nomad_upload_metadata import (
    ROD_CITING_WIKI_URL,
    write_nomad_json,
)
from pynxtools_raman.rod.rod_reader import ROD_CITATION_DOI, ROD_LICENSE_TEXT


def test_write_nomad_json_creates_file_with_expected_name(tmp_path):
    output_path = write_nomad_json(tmp_path)

    assert output_path == tmp_path / "nomad.json"
    assert output_path.is_file()


def test_write_nomad_json_content_is_valid_json_with_expected_keys(tmp_path):
    output_path = write_nomad_json(tmp_path)

    metadata = json.loads(output_path.read_text(encoding="utf-8"))

    assert set(metadata.keys()) == {"comment", "references"}
    assert isinstance(metadata["comment"], str)
    assert isinstance(metadata["references"], list)


def test_comment_cites_rod_and_its_license(tmp_path):
    output_path = write_nomad_json(tmp_path)
    metadata = json.loads(output_path.read_text(encoding="utf-8"))

    assert "Raman Open Database" in metadata["comment"]
    assert ROD_LICENSE_TEXT in metadata["comment"]
    assert ROD_CITATION_DOI in metadata["comment"]


def test_references_include_doi_wiki_and_license_urls(tmp_path):
    output_path = write_nomad_json(tmp_path)
    metadata = json.loads(output_path.read_text(encoding="utf-8"))

    assert f"https://doi.org/{ROD_CITATION_DOI}" in metadata["references"]
    assert ROD_CITING_WIKI_URL in metadata["references"]
    assert (
        "https://creativecommons.org/publicdomain/zero/1.0/" in (metadata["references"])
    )
