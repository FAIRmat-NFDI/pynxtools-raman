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
"""Writes the nomad.json upload metadata file and README.md for a batch of
ROD-derived NeXus files.

NOMAD reads a nomad.json/nomad.yaml bundled inside an upload's own raw files
(at any directory level) as *user metadata* -- comment, references,
coauthors, datasets, per-entry overrides -- applied during the initial
processing of the entries beneath it. nomad.json is used here specifically
to avoid naming collisions with a NOMAD deployment's nomad.yaml.

nomad.json carries the ROD-wide (dataset-level) citation and license. It is
distinct from the per-entry citeID(NXcite) groups written into each .nxs
file, which cite the individual publication and ROD record. README.md
carries the same citation/license information in human-readable form, plus
a list of which .nxs files are included in this particular upload.
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


def write_readme(nxs_filenames: list[str], output_dir: Path) -> Path:
    """Write README.md (a human-readable description of this upload) into
    output_dir, returning the path written.

    Args:
        nxs_filenames (list[str]): Names of the .nxs files included in this
            upload -- listed in the README so the contents of a batch are
            clear without having to open the archive.
        output_dir (Path): Directory to write README.md into.
    """
    file_list = "\n".join(f"- `{name}`" for name in sorted(nxs_filenames))
    content = (
        "# Raman Open Database -- NOMAD upload\n\n"
        f"This upload contains {len(nxs_filenames)} Raman spectra sourced "
        "from the [Raman Open Database (ROD)]"
        "(https://solsa.crystallography.net/rod/), converted to NeXus "
        "(NXraman) by "
        "[pynxtools-raman](https://github.com/FAIRmat-NFDI/pynxtools-raman).\n\n"
        f"{ROD_LICENSE_TEXT} Please cite the database: {ROD_CITATION_TEXT}\n\n"
        "See `nomad.json` for the same citation/license metadata in the form "
        "NOMAD applies to each entry.\n\n"
        "## Files in this upload\n\n"
        f"{file_list}\n"
    )
    output_path = output_dir / "README.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path
