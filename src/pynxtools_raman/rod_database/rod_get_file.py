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
import logging
from pathlib import Path

import requests

logger = logging.getLogger(__file__)


def save_rod_file_from_ROD_via_API(
    rod_id: int, output_dir: Path | None = None
) -> Path | None:
    """Download a .rod file from the Raman Open Database.

    Args:
        rod_id (int): ROD record ID to download.
        output_dir (Path, optional): Directory to write the .rod file
            into. Created if it doesn't exist yet. Defaults to the
            current directory.

    Returns:
        Optional[Path]: Path of the downloaded file, or None if the
            download failed (the error is logged, not raised).
    """
    url = "https://solsa.crystallography.net/rod/" + str(rod_id) + ".rod"
    output_dir = output_dir or Path()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Initialized download of .rod file with ID '{rod_id}' from '{url}'.")

    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise HTTP error for bad

        logger.info(f"Successfully received .rod file with ID '{rod_id}'")

        file_path = output_dir / f"{rod_id}.rod"
        file_path.write_text(response.text, encoding="utf-8")
        logger.info(f"Saved .rod file with ID '{rod_id}' to file '{file_path}'")
        return file_path

    except requests.exceptions.ConnectionError as con_err:
        logger.error(f"ConnectionError occurred: {con_err}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"CHTTPError occurred: {http_err}")
    except requests.exceptions.RequestException as req_exc:
        logger.error(f"RequestException occurred: {req_exc}")
    return None
