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
"""CLI tests for the top-level ``pynx-raman`` dispatcher."""

import pytest
from click.testing import CliRunner

from pynxtools_raman.cli import pynx_raman


@pytest.fixture()
def runner():
    return CliRunner()


class TestPynxRamanGroup:
    def test_lists_all_subcommands(self, runner):
        result = runner.invoke(pynx_raman, ["--help"])
        assert result.exit_code == 0
        for name in ("download", "build-upload-batch", "analyze-keys"):
            assert name in result.output

    def test_unknown_command_fails(self, runner):
        result = runner.invoke(pynx_raman, ["does-not-exist"])
        assert result.exit_code != 0

    def test_download_and_build_upload_batch_share_options(self, runner):
        # Both commands share the rod_batch_options decorator, so their
        # --help output should list the same flags.
        for name in ("download", "build-upload-batch"):
            result = runner.invoke(pynx_raman, [name, "--help"])
            assert result.exit_code == 0
            for flag in ("ROD_IDS", "--ids-file", "--all", "--output-dir", "--yes"):
                assert flag in result.output, f"{flag} missing from '{name} --help'"

    def test_analyze_keys_subcommand_help(self, runner):
        result = runner.invoke(pynx_raman, ["analyze-keys", "--help"])
        assert result.exit_code == 0
        assert "ROD_DIR" in result.output
