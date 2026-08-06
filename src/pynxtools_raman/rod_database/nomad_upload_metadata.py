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
"""Writes the nomad.json upload metadata file for a batch of ROD-derived
NeXus files.

NOMAD reads a nomad.json/nomad.yaml bundled inside an upload's own raw files
(at any directory level) as *user metadata* -- comment, references,
coauthors, datasets, per-entry overrides -- applied during the initial
processing of the entries beneath it. nomad.json is used here specifically
to avoid naming collisions with a NOMAD deployment's nomad.yaml.

This file carries the ROD-wide (dataset-level) citation and license. It is
distinct from the per-entry citeID(NXcite) groups written into each .nxs
file, which cite the individual publication and ROD record.
"""

import json
from pathlib import Path

from pynxtools_raman.parsers.rod import (
    ROD_CITATION_DOI,
    ROD_CITATION_TEXT,
    ROD_LICENSE_TEXT,
)

ROD_CITING_WIKI_URL = "https://wiki.crystallography.net/rod/citing/"
CC0_LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"

UPLOAD_METADATA: dict = {
    "comment": (
        "Contains Raman spectra sourced from the Raman Open Database (ROD, "
        "https://solsa.crystallography.net/rod/). "
        f"{ROD_LICENSE_TEXT} Please cite the database: {ROD_CITATION_TEXT}"
    ),
    "references": [
        f"https://doi.org/{ROD_CITATION_DOI}",
        ROD_CITING_WIKI_URL,
        CC0_LICENSE_URL,
    ],
}


def write_nomad_json(output_dir: Path) -> Path:
    """Write nomad.json (the ROD-wide citation/license upload metadata) into
    output_dir, returning the path written.
    """
    output_path = output_dir / "nomad.json"
    output_path.write_text(
        json.dumps(UPLOAD_METADATA, indent=2) + "\n", encoding="utf-8"
    )
    return output_path
