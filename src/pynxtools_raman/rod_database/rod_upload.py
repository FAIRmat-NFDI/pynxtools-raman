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
"""Upload a ROD batch (produced by build_rod_upload_batch) to NOMAD via
nomad-utility-workflows.

nomad_utility_workflows is imported lazily inside each function, not at
module level: it reads NOMAD_USERNAME/NOMAD_PASSWORD from the environment
at import time and raises if they're unset, which would otherwise break
every pynx-raman command (not just upload) the moment this module is
imported.
"""

import logging
import shutil
import time
from pathlib import Path

import click

logger = logging.getLogger(__file__)


def zip_upload_batch(directory: Path, zip_path: Path | None = None) -> Path:
    """Zip directory's contents into a single archive ready for NOMAD
    upload, defaulting to <directory>.zip.

    Args:
        directory (Path): Directory whose contents to zip.
        zip_path (Path, optional): Path of the resulting archive. Defaults
            to directory with a .zip suffix.

    Returns:
        Path: Path of the written zip file.
    """
    zip_path = zip_path or directory.with_suffix(".zip")
    base_name = str(zip_path.with_suffix(""))
    archive = shutil.make_archive(base_name, "zip", root_dir=directory)
    return Path(archive)


def _import_nomad_utility_workflows():
    try:
        from nomad_utility_workflows.utils import uploads  # noqa: PLC0415

        return uploads
    except Exception as exc:
        raise click.UsageError(
            "Could not initialize the NOMAD upload client. Make sure "
            "NOMAD_USERNAME and NOMAD_PASSWORD are set in the environment."
        ) from exc


def upload_batch(zip_path: Path, url: str | None = None) -> str:
    """Upload zip_path to NOMAD.

    Args:
        zip_path (Path): Path of the zip file to upload.
        url (str, optional): NOMAD API URL. Defaults to the central NOMAD
            deployment (nomad-utility-workflows' own default).

    Returns:
        str: The new upload's ID.

    Raises:
        click.UsageError: If NOMAD_USERNAME/NOMAD_PASSWORD aren't set.
    """
    uploads = _import_nomad_utility_workflows()

    upload_id = uploads.upload_files_to_nomad(str(zip_path), url=url)
    logger.info(f"Created upload {upload_id} from {zip_path}.")

    return upload_id


def set_upload_name(upload_id: str, upload_name: str, url: str | None = None) -> None:
    """Set upload_id's name.

    NOMAD rejects a metadata edit while an upload is still processing (a
    server-side race, not something this function can work around), so
    call this after wait_for_processing(), not right after upload_batch().

    Args:
        upload_id (str): The upload to rename.
        upload_name (str): Name to give the upload.
        url (str, optional): NOMAD API URL.
    """
    uploads = _import_nomad_utility_workflows()
    uploads.edit_upload_metadata(
        upload_id, upload_metadata={"upload_name": upload_name}, url=url
    )
    logger.info(f"Set upload {upload_id}'s name to {upload_name!r}.")


def wait_for_processing(
    upload_id: str, url: str | None = None, poll_interval_s: float = 5.0
):
    """Poll the upload's processing status until it's no longer running,
    logging progress as it goes.

    Args:
        upload_id (str): The upload to poll.
        url (str, optional): NOMAD API URL.
        poll_interval_s (float): Seconds to wait between polls.

    Returns:
        NomadUpload: The upload's final state, including any errors.
    """
    uploads = _import_nomad_utility_workflows()

    upload = uploads.get_upload_by_id(upload_id, url=url)
    while upload.process_running:
        time.sleep(poll_interval_s)
        upload = uploads.get_upload_by_id(upload_id, url=url)
        logger.info(f"Upload {upload_id}: {upload.process_status}")

    return upload


def publish_batch_upload(upload_id: str, url: str | None = None) -> None:
    """Publish the given upload, making it public.

    Args:
        upload_id (str): The upload to publish.
        url (str, optional): NOMAD API URL.
    """
    uploads = _import_nomad_utility_workflows()
    uploads.publish_upload(upload_id, url=url)
    logger.info(f"Published upload {upload_id}.")
