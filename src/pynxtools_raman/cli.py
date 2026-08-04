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
"""Top-level ``pynx-raman`` CLI dispatcher.

All pynxtools-raman command-line tools are available under this single
entry point, mirroring the top-level ``pynx`` dispatcher in pynxtools::

    pynx-raman download [ROD_IDS...]            # download a batch of .rod files
    pynx-raman build-upload-batch [ROD_IDS...]  # download, convert, and stamp a NOMAD upload batch
    pynx-raman analyze-keys [ROD_DIR]           # count CIF key frequency across a directory

``download`` and ``build-upload-batch`` share the same options
(--ids-file, --all, --output-dir, --yes/-y); ``analyze-keys`` defaults to
the same directory (rod_batch) and writes its report there too.
"""

import click

from pynxtools_raman.rod.rod_batch import build_rod_upload_batch, download_rod_files_cli
from pynxtools_raman.rod.rod_stats import analyze_rod_keys


@click.group()
def pynx_raman():
    """pynxtools-raman command-line tools.

    Use ``pynx-raman COMMAND --help`` for details on each sub-command.
    """


pynx_raman.add_command(download_rod_files_cli, name="download")
pynx_raman.add_command(build_rod_upload_batch, name="build-upload-batch")
pynx_raman.add_command(analyze_rod_keys, name="analyze-keys")
