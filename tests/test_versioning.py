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
"""The old versioning module is deprecated and gives the core helpers."""

import importlib

import pytest
from pynxtools.dataconverter.readers.parsers import versioning as core_versioning

HELPERS = [
    "VersionRange",
    "VersionTuple",
    "format_version",
    "format_version_ranges",
    "is_version_supported",
    "normalize_version",
    "version_ranges_overlap",
]


def test_old_versioning_module_warns_and_gives_the_core_helpers():
    """The old module still works, but tells users to import from core."""
    with pytest.warns(DeprecationWarning, match="is deprecated"):
        old_module = importlib.reload(
            importlib.import_module("pynxtools_raman.parsers.versioning")
        )
    for name in HELPERS:
        assert getattr(old_module, name) is getattr(core_versioning, name)
