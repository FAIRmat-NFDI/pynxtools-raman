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
"""Tests for the config files: the shipped configs are valid JSON, and a
config file given by the user is not replaced by the built-in one."""

import json
from pathlib import Path

import pytest

import pynxtools_raman
from pynxtools_raman.reader import RamanReader

CONFIG_DIR = Path(pynxtools_raman.__file__).parent / "config"
CONFIG_FILES = sorted(CONFIG_DIR.glob("*.json"))

DATA = Path(__file__).parent / "data"
DATA_FILES = {
    "witec": [
        str(DATA / "witec" / "Si-wafer-Raman-Spectrum-1.txt"),
        str(DATA / "witec" / "eln_data.yaml"),
    ],
    "rod": [str(DATA / "rod" / "rod_file_1000679.rod")],
}


@pytest.fixture
def user_config(tmp_path):
    config = tmp_path / "my_config.json"
    config.write_text(json.dumps({"/ENTRY[entry]/title": "from my config"}))
    return config


@pytest.mark.parametrize("data_files", DATA_FILES.values(), ids=DATA_FILES.keys())
@pytest.mark.parametrize("how", ["config_file kwarg", "json in file list"])
def test_user_config_is_used(data_files, how, user_config):
    reader = RamanReader()
    if how == "config_file kwarg":
        output = reader.read(file_paths=data_files, config_file=user_config)
    else:
        output = reader.read(file_paths=[*data_files, str(user_config)])

    assert Path(reader.config_file) == user_config
    assert output["/ENTRY[entry]/title"] == "from my config"


@pytest.mark.parametrize("data_files", DATA_FILES.values(), ids=DATA_FILES.keys())
def test_builtin_config_without_user_config(data_files):
    reader = RamanReader()
    reader.read(file_paths=data_files)

    assert Path(reader.config_file).parent.name == "config"


def test_config_files_are_found():
    assert CONFIG_FILES


@pytest.mark.parametrize("config_file", CONFIG_FILES, ids=lambda path: path.name)
def test_config_file_is_valid_json(config_file):
    with open(config_file, encoding="utf-8") as file:
        json.load(file)
