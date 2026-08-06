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
"""Utilities for declaring and checking parser format-version support.

None of the supported formats has a known, observed version story
today, so no parser currently overrides ``RamanParser.detect_version`` or
sets a non-empty ``supported_versions``. This module exists so that when a
real version-limited format variant does show up, version support can be
added to a parser without reshaping the base class.
"""

from collections.abc import Iterable
from typing import TypeAlias

VersionTuple: TypeAlias = tuple[int | str, ...]
VersionRange: TypeAlias = tuple[VersionTuple, VersionTuple | None]


def _format_version(version: VersionTuple) -> str:
    return ".".join(str(x) for x in version)


def is_version_supported(
    version: VersionTuple | None,
    supported_versions: Iterable[VersionRange],
) -> bool:
    """
    Determine whether a version tuple falls within the supported ranges.

    ``supported_versions`` is an iterable of half-open intervals
    ``(lower_inclusive, upper_exclusive_or_None)``. An empty iterable means
    no version constraint: all files are accepted, including those without
    a detected version. A non-empty iterable implicitly requires a version;
    ``None`` is rejected because it cannot fall within any declared range.
    """
    ranges = tuple(supported_versions)
    if not ranges:
        return True

    if version is None:
        return False

    for lower, upper in ranges:
        if upper is None:
            if version >= lower:
                return True
        elif lower <= version < upper:
            return True

    return False
