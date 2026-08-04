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
"""Bulk download and NOMAD-upload-batch pipeline for ROD records.

Both sub-commands here (``download``, ``build-upload-batch``) operate on the
same kind of input -- a batch of ROD IDs, given directly, via --ids-file,
and/or via --all -- so they share one option surface (rod_batch_options)
and one ID-resolution/confirmation path, rather than duplicating that
across each command.
"""

import logging
from collections.abc import Callable
from pathlib import Path

import click
from pynxtools.dataconverter.convert import convert

from pynxtools_raman.rod.nomad_upload_metadata import write_nomad_json
from pynxtools_raman.rod.rod_get_file import (
    DEFAULT_ROD_BATCH_DIR,
    save_rod_file_from_ROD_via_API,
)

logger = logging.getLogger(__file__)

DATA_DIR = Path(__file__).parent / "data"
ALL_KNOWN_ROD_IDS_FILE = DATA_DIR / "ROD-numbers.txt"


def missing_rod_ids(rod_ids: list[int], output_dir: Path) -> list[int]:
    """Return the subset of rod_ids that don't already have a .rod file in
    output_dir -- the ones a download would actually have to fetch.
    """
    return [
        rod_id for rod_id in rod_ids if not (output_dir / f"{rod_id}.rod").is_file()
    ]


def download_rod_files(rod_ids: list[int], output_dir: Path) -> list[Path]:
    """Download a batch of .rod files by ROD ID into output_dir.

    IDs whose .rod file already exists in output_dir are skipped without
    re-requesting them. IDs that fail to download are logged (by
    save_rod_file_from_ROD_via_API) and skipped rather than raised, so one
    bad ID doesn't abort the batch.

    Args:
        rod_ids (list[int]): ROD record IDs to download.
        output_dir (Path): Directory to write the .rod files into.

    Returns:
        list[Path]: Paths of all .rod files present in output_dir
            afterwards (both newly downloaded and already-existing).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for rod_id in rod_ids:
        existing = output_dir / f"{rod_id}.rod"
        if existing.is_file():
            logger.info(f"'{existing}' already exists, skipping download.")
            paths.append(existing)
            continue
        path = save_rod_file_from_ROD_via_API(rod_id, output_dir=output_dir)
        if path is not None:
            paths.append(path)
    return paths


def convert_rod_files(input_dir: Path, output_dir: Path | None = None) -> list[Path]:
    """Convert all ``.rod`` files in ``input_dir`` to ``.nxs`` files.

    The converted files are written to ``output_dir`` (default: ``input_dir``)
    using the Raman reader. Output files have the same stem as their
    corresponding input files.

    Files that fail to convert are logged and skipped.
    """
    output_dir = output_dir or input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = []
    for rod_file in sorted(input_dir.glob("*.rod")):
        output_file = output_dir / f"{rod_file.stem}.nxs"
        try:
            convert(
                input_file=(str(rod_file),),
                reader="raman",
                nxdl="NXraman",
                output=str(output_file),
            )
            converted.append(output_file)
        except Exception:
            logger.exception(f"Failed to convert {rod_file} to NeXus.")
    return converted


def collect_rod_ids(rod_ids: list[str], ids_file: Path | None) -> list[int]:
    """Combine explicitly given ROD IDs with IDs read from ids_file (one per
    line, e.g. ROD-numbers.txt).
    """
    collected = [int(rod_id) for rod_id in rod_ids]
    if ids_file is not None:
        collected += [
            int(line.strip())
            for line in ids_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return collected


def resolve_rod_ids(
    rod_ids: tuple[str, ...], ids_file: Path | None, all_known: bool
) -> list[int]:
    """Resolve the final, deduplicated list of ROD IDs a command should act
    on, combining positional IDs, --ids-file, and --all (the bundled full
    ID list). Raises click.UsageError if the result is empty.
    """
    rod_id_list = collect_rod_ids(list(rod_ids), ids_file)
    if all_known:
        rod_id_list = list(
            dict.fromkeys(rod_id_list + collect_rod_ids([], ALL_KNOWN_ROD_IDS_FILE))
        )
    if not rod_id_list:
        raise click.UsageError(
            "No ROD IDs given (pass IDs directly, via --ids-file, or --all)."
        )
    return rod_id_list


def confirm_download(rod_id_list: list[int], output_dir: Path, yes: bool) -> bool:
    """Ask for confirmation before downloading whichever of rod_id_list
    aren't already present in output_dir, unless yes is set. Skips the
    prompt entirely (no network activity, nothing to confirm) if every ID
    already has a .rod file there. Returns whether the caller should
    proceed.
    """
    if yes:
        return True
    to_download = missing_rod_ids(rod_id_list, output_dir)
    if not to_download:
        return True
    if click.confirm(
        f"About to download {len(to_download)} .rod file(s) into {output_dir}. Proceed?"
    ):
        return True
    click.echo("Cancelled.")
    return False


def rod_batch_options(command: Callable) -> Callable:
    """Shared CLI surface for commands operating on a batch of ROD IDs:
    positional IDs, --ids-file, --all, --output-dir, --yes.
    """
    command = click.argument("rod_ids", nargs=-1)(command)
    command = click.option(
        "--ids-file",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
        default=None,
        help="Text file with one ROD ID per line, e.g. ROD-numbers.txt.",
    )(command)
    command = click.option(
        "--all",
        "all_known",
        is_flag=True,
        help=(
            f"Use the full list of known ROD IDs bundled with this package "
            f"({ALL_KNOWN_ROD_IDS_FILE.name}), in addition to any given via "
            "ROD_IDS/--ids-file."
        ),
    )(command)
    command = click.option(
        "--output-dir",
        type=click.Path(file_okay=False, path_type=Path),
        default=DEFAULT_ROD_BATCH_DIR,
        show_default=True,
        help="Directory the .rod files (and any further output) are written into.",
    )(command)
    command = click.option(
        "--yes",
        "-y",
        is_flag=True,
        help="Do not ask for confirmation before downloading.",
    )(command)
    return command


@click.command("download-rod-files")
@rod_batch_options
def download_rod_files_cli(
    rod_ids: tuple[str, ...],
    ids_file: Path | None,
    all_known: bool,
    output_dir: Path,
    yes: bool,
):
    """Download a batch of .rod files from the Raman Open Database.

    ROD_IDS: ROD IDs to download, in addition to any given via --ids-file
    and/or --all.
    """
    rod_id_list = resolve_rod_ids(rod_ids, ids_file, all_known)
    if not confirm_download(rod_id_list, output_dir, yes):
        return

    downloaded = download_rod_files(rod_id_list, output_dir)
    click.echo(
        f"{len(downloaded)}/{len(rod_id_list)} .rod file(s) present in {output_dir}."
    )


@click.command("build-rod-upload-batch")
@rod_batch_options
def build_rod_upload_batch(
    rod_ids: tuple[str, ...],
    ids_file: Path | None,
    all_known: bool,
    output_dir: Path,
    yes: bool,
):
    """Download, convert, and add nomad.json upload metadata for a batch of
    ROD records -- the full pipeline for one NOMAD upload, ready to zip.

    ROD_IDS: ROD IDs to include, in addition to any given via --ids-file
    and/or --all.
    """
    rod_id_list = resolve_rod_ids(rod_ids, ids_file, all_known)
    if not confirm_download(rod_id_list, output_dir, yes):
        return

    downloaded = download_rod_files(rod_id_list, output_dir)
    click.echo(
        f"{len(downloaded)}/{len(rod_id_list)} .rod file(s) present in {output_dir}."
    )

    converted = convert_rod_files(output_dir)
    click.echo(f"Converted {len(converted)} .rod file(s) to NeXus.")

    metadata_path = write_nomad_json(output_dir)
    click.echo(
        f"Wrote {metadata_path}. Batch ready in {output_dir} -- zip it for upload."
    )
