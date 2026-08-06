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
"""Abstract base class for raman file-format parsers (.rod, WITec .txt, ...)."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

from pynxtools_raman.parsers.versioning import (
    VersionRange,
    VersionTuple,
    is_version_supported,
)

__all__: list[str] = []


class _RamanParser(ABC):
    """
    Base class every raman sub-reader parser subclasses.

    A parser populates three plain dict attributes while parsing a file:
        - ``attrs``: scalar metadata (instrument settings, sample info, ...),
          looked up via the config file's ``@attrs:`` prefix.
        - ``data``: measurement data (spectrum arrays), looked up via ``@data:``.
        - ``unused_attrs``: entries of ``attrs`` not yet claimed by any
          ``@attrs:`` reference in the config file. ``RamanReader`` writes
          whatever remains here into a ``COLLECTION[<unused_attrs_group_name>]``
          catch-all group, so nothing is silently dropped.

    These are plain mutable attributes, not copied: ``RamanReader`` aliases
    its own ``attrs``/``data``/``missing_meta_data`` to the active parser's
    ``attrs``/``data``/``unused_attrs``, so ``post_process`` mutating them
    in place is automatically visible reader-side.
    """

    supported_file_extensions: ClassVar[tuple[str, ...]] = ()
    # No raman format has a known, observed version story today - see
    # parsers/versioning.py's module docstring for why this is here anyway.
    supported_versions: ClassVar[tuple[VersionRange, ...]] = ()
    supported_vendor: ClassVar[str | None] = None
    config_file: ClassVar[str] = ""  # filename under config/
    unused_attrs_group_name: ClassVar[str] = "unused_data"

    def __init__(self) -> None:
        self.file: Path | None = None
        self.attrs: dict[str, Any] = {}
        self.data: dict[str, Any] = {}
        self.unused_attrs: dict[str, Any] = {}

    @classmethod
    def is_extension_supported(cls, file: Path) -> bool:
        suffix = file.suffix.lower()
        return any(suffix == ext.lower() for ext in cls.supported_file_extensions)

    @classmethod
    def is_version_supported(cls, version: VersionTuple | None) -> bool:
        return is_version_supported(version, cls.supported_versions)

    def detect_version(self, file: Path) -> VersionTuple | None:
        """Detect this file's format version. Override in subclasses that
        have one to detect; the default means "no version concept"."""
        return None

    @abstractmethod
    def matches_file(self, file: Path) -> bool:
        """
        Return True if `file` structurally matches this parser's format.

        Implementations must perform positive identification - not just an
        extension check. Keep it cheap (read at most a few KB), and always
        catch exceptions internally and return False rather than raising.
        """

    def _is_mainfile(self, file: Path) -> None:
        """Raise ValueError with a specific reason if `file` isn't supported
        by this parser; return normally if it is."""
        if not self.is_extension_supported(file):
            allowed = ", ".join(self.supported_file_extensions) or "<none>"
            raise ValueError(
                f"Cannot process file '{file.name}' (extension "
                f"'{file.suffix or '<none>'}'). {type(self).__name__} only "
                f"supports: {allowed}."
            )

        version = self.detect_version(file)
        if not self.is_version_supported(version):
            raise ValueError(
                f"File '{file.name}' has an unsupported version "
                f"({version if version is not None else '<unknown>'}) for "
                f"{type(self).__name__}."
            )

        if not self.matches_file(file):
            raise ValueError(
                f"File '{file.name}' does not match the expected format "
                f"for {type(self).__name__}."
            )

    @classmethod
    def is_mainfile(cls, file: str | Path) -> bool:
        """
        Safe, non-raising check: does this parser support `file`?

        Call this before `parse()` to decide whether to parse a file at
        all - a file that fails this check must not be parsed.
        """
        try:
            cls()._is_mainfile(Path(file))
            return True
        except ValueError:
            return False

    def parse(self, file: str | Path, **kwargs) -> None:
        """Parse `file`, populating self.attrs / self.data / self.unused_attrs
        in place. Raises ValueError if `file` doesn't match this parser -
        callers should normally already have checked `is_mainfile()` first."""
        file = Path(file)
        self.file = file
        self._is_mainfile(file)
        self._parse(file, **kwargs)

    @abstractmethod
    def _parse(self, file: Path, **kwargs) -> None:
        """Populate self.attrs / self.data / self.unused_attrs. Implemented
        by subclasses."""

    def post_process(self, eln_data: dict[str, Any]) -> None:
        """Derive fields that need config/ELN context, after all input
        files have been read. Default no-op; override per-parser. Mutates
        self.attrs / self.data / self.unused_attrs in place."""
        return None
