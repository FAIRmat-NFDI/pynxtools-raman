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
"""An example reader implementation based on the MultiFormatReader."""

import logging
from pathlib import Path
from typing import Any

from pynxtools.dataconverter.readers.multi.reader import MultiFormatReader
from pynxtools.dataconverter.readers.utils import parse_yml

from pynxtools_raman.parsers import RodParser, WitecParser, _RamanParser

logger = logging.getLogger("pynxtools")

CONVERT_DICT: dict[str, str] = {}

REPLACE_NESTED: dict[str, str] = {}


class RamanReader(MultiFormatReader):
    """MyDataReader implementation for the DataConverter to convert mydata to NeXus."""

    supported_nxdls = ["NXraman"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs: dict[str, Any] = {}
        self.data: dict[str, Any] = {}
        self.eln_data: dict[str, Any] = {}
        self.config_file: Path

        self.missing_meta_data: dict[str, Any] | None = None
        self._active_parser: _RamanParser | None = None
        self._unused_attrs_group_name: str | None = None

        self.extensions = {
            ".yml": self.handle_eln_file,
            ".yaml": self.handle_eln_file,
            ".txt": self.handle_txt_file,
            ".json": self.set_config_file,
            ".rod": self.handle_rod_file,
        }

    def set_config_file(self, file_path: Path) -> dict[str, Any]:
        if self.config_file is not None:
            logger.info(
                f"Config file already set. Replaced by the new file {file_path}."
            )
        self.config_file = file_path
        return {}

    def handle_eln_file(self, file_path: str) -> dict[str, Any]:
        self.eln_data = parse_yml(
            file_path,
            convert_dict=CONVERT_DICT,
            parent_key="/ENTRY[entry]",
        )

        return {}

    def _set_parser_data(self, parser) -> None:
        """Populate reader state from a parsed file."""
        reader_dir = Path(__file__).parent
        self.config_file = reader_dir.joinpath("config", parser.config_file)  # pylint: disable=invalid-type-comment
        self._active_parser = parser
        self._unused_attrs_group_name = parser.unused_attrs_group_name
        self.attrs = parser.attrs
        self.data = parser.data
        self.missing_meta_data = parser.unused_attrs

    def handle_rod_file(self, filepath) -> dict[str, Any]:
        """
        Read a .rod file (Raman Open Database) via RodParser.
        """
        if not RodParser.is_mainfile(filepath):
            logger.warning(f"{filepath} does not look like a ROD .rod file; skipping.")
            return {}

        parser = RodParser()
        parser.parse(filepath)

        if parser.attrs.get("_raman_theoretical_spectrum.intensity"):
            logger.warning(
                "Theoretical Raman data .rod file found. File parsing aborted."
            )
            # Prevent file parsing from setting an invalid config file name.
            self.config_file = Path()
            return {}

        self._set_parser_data(parser)
        return {}

    def handle_txt_file(self, filepath) -> dict[str, Any]:
        """
        Read a .txt file from a WITec Alpha Raman spectrometer via WitecParser.
        """
        if not WitecParser.is_mainfile(filepath):
            logger.warning(
                f"{filepath} does not look like a WITec .txt export; skipping."
            )
            return {}

        parser = WitecParser()
        parser.parse(filepath)

        self._set_parser_data(parser)
        return {}

    def get_eln_data(self, key: str, path: str) -> Any:
        """
        Returns data from the eln file. This is done via the file: "config_file.json".
        There are two situations:
            1. The .json file has only a key assigned
            2. The .json file has a key AND a value assigned.
        The assigned value should be a "path", which reflects another entry in the eln file.
        This acts as eln_path redirection, which is used for example to assign flexible
        parameters from the eln_file (units, axisnames, etc.)
        """
        if self.eln_data is None:
            return None

        # Use the path to get the eln_data (this refers to the 2. case)
        if len(path) > 0:
            return self.eln_data.get(path)

        # If no path is assigned, use directly the given key to extract
        # the eln data/value (this refers to the 1. case)

        # Filtering list, for NeXus concepts which use mixed notation of
        # upper and lowercase to ensure correct NXclass labeling.
        upper_and_lower_mixed_nexus_concepts = [
            "/detector_TYPE[",
            "/beam_TYPE[",
            "/source_TYPE[",
            "/polfilter_TYPE[",
            "/spectral_filter_TYPE[",
            "/temp_control_TYPE[",
            "/software_TYPE[",
            "/OPTICAL_LENS[",
            "/identifierNAME[",
        ]
        if self.eln_data.get(key) is None:
            # filter for mixed concept names
            for string in upper_and_lower_mixed_nexus_concepts:
                key = key.replace(string, "/[")
            # add only characters, if they are lower case and if they are not "[" or "]"
            result = "".join(
                [char for char in key if not (char.isupper() or char in "[]")]
            )
            # Filter as well for
            result = result.replace("entry", f"ENTRY[{self.callbacks.entry_name}]")

            if self.eln_data.get(result) is not None:
                return self.eln_data.get(result)
            else:
                logger.warning(
                    f"No key found during eln_data processing for key '{key}' after it's modification to '{result}'."
                )
        return self.eln_data.get(key)

    def get_attr(self, key: str, path: str) -> Any:
        """
        Returns scalar metadata (instrument settings, sample info, ...) for
        the "@attrs:" config file prefix, looked up in self.attrs.
        """
        value = self.attrs.get(path)

        # this filters out the meta data, which is up to now only created for .rod files

        if (path is None or path == "") and key is not None:
            return self.attrs.get(key)

        if self.missing_meta_data:
            # this if condition is required, to only delete keys which are available by the data.
            # e.g. is defined to extract it via config.json, but there is no value in meta data
            if path in self.missing_meta_data.keys():
                del self.missing_meta_data[path]

        if value is not None:
            try:
                # ensure that the space_group entry from NXsample is of type
                # NXchar, even if space group numbers are used
                if "/space_group" in key and "/SAMPLE" in key:
                    return value
                return float(value)
            except (ValueError, TypeError):
                return self.attrs.get(path)
        else:
            logger.warning(f"No axis name corresponding to the path {path}.")

    def get_data(self, key: str, path: str) -> Any:
        """
        Returns measurement data (spectrum arrays) for the "@data:" config
        file prefix, looked up in self.data. Unlike self.attrs, entries here
        are never candidates for the unused-keys collection.
        """
        return self.data.get(path or key)

    def post_process(self) -> None:
        """
        Runs once, after ALL input files (including the ELN) have been
        processed, regardless of file order - see MultiFormatReader.read().
        It runs the `post_process` hook of the active parser.
        """
        if self._active_parser is not None:
            self._active_parser.post_process(self.eln_data)

    def read(
        self,
        template: dict = None,
        file_paths: tuple[str] = None,
        objects: tuple[Any] = None,
        **kwargs,
    ) -> dict:
        template = super().read(template, file_paths, objects, suppress_warning=True)
        # set default data

        if self.missing_meta_data:
            group = self._unused_attrs_group_name or "unused_data"
            for key in self.missing_meta_data:
                template[
                    f"/ENTRY[{self.callbacks.entry_name}]/COLLECTION[{group}]/{key}"
                ] = f"{self.missing_meta_data[key]}"

        template["/@default"] = "entry"

        return template


READER = RamanReader
