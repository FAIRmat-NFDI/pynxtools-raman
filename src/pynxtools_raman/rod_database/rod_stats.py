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
"""Reports how often each CIF key occurs across a directory of .rod files.

Useful when extending config_file_rod.json: shows which CIF keys are
common (worth mapping) versus rare across a corpus of downloaded ROD
records.
"""

from pathlib import Path

import click

from pynxtools_raman.parsers.rod import RodParser
from pynxtools_raman.rod_database import DEFAULT_ROD_BATCH_DIR


def count_rod_keys(rod_dir: Path) -> dict[str, int]:
    """Count how many .rod files in rod_dir contain each CIF key, sorted by
    descending frequency.
    """
    key_counts: dict[str, int] = {}
    for rod_file in sorted(rod_dir.glob("*.rod")):
        parser = RodParser()
        parser.get_cif_file_content(str(rod_file))
        for key in parser.extract_keys_and_values_from_cif():
            key_counts[key] = key_counts.get(key, 0) + 1
    return dict(sorted(key_counts.items(), key=lambda item: item[1], reverse=True))


@click.command("analyze-rod-keys")
@click.argument(
    "rod_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=DEFAULT_ROD_BATCH_DIR,
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="File to write the key/count report to (default: rod_key_statistics.txt inside ROD_DIR).",
)
def analyze_rod_keys(rod_dir: Path, output: Path | None):
    """Count how often each CIF key occurs across every .rod file in ROD_DIR,
    writing a sorted key/count report into ROD_DIR.

    ROD_DIR: directory containing .rod files (default: rod_batch).
    """
    output = output or (rod_dir / "rod_key_statistics.txt")
    key_counts = count_rod_keys(rod_dir)
    output.write_text(
        "".join(f"{key}\t{count}\n" for key, count in key_counts.items()),
        encoding="utf-8",
    )
    n_files = sum(1 for _ in rod_dir.glob("*.rod"))
    click.echo(
        f"Found {len(key_counts)} distinct keys across {n_files} file(s). "
        f"Wrote report to {output}."
    )
