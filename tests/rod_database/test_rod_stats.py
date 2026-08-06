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
"""Tests for the ROD CIF-key frequency report (rod_stats.py)."""

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from pynxtools_raman.rod_database import DEFAULT_ROD_BATCH_DIR
from pynxtools_raman.rod_database.rod_stats import analyze_rod_keys, count_rod_keys

ROD_FIXTURE = Path(__file__).parents[1] / "data" / "rod" / "rod_file_1000679.rod"


@pytest.fixture()
def runner():
    return CliRunner()


class TestCountRodKeys:
    def test_counts_keys_in_a_single_file(self, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "rod_file_1000679.rod")

        counts = count_rod_keys(tmp_path)

        assert counts["_publ_author_name"] == 1
        assert counts["_rod_database.code"] == 1

    def test_counts_keys_across_multiple_files(self, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "a.rod")
        shutil.copy(ROD_FIXTURE, tmp_path / "b.rod")

        counts = count_rod_keys(tmp_path)

        assert counts["_publ_author_name"] == 2

    def test_sorted_by_descending_frequency(self, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "a.rod")
        shutil.copy(ROD_FIXTURE, tmp_path / "b.rod")

        counts = count_rod_keys(tmp_path)

        assert list(counts.values()) == sorted(counts.values(), reverse=True)

    def test_empty_directory_returns_empty_dict(self, tmp_path):
        assert count_rod_keys(tmp_path) == {}


class TestAnalyzeRodKeysCli:
    def test_writes_report_file_at_explicit_output(self, runner, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "rod_file_1000679.rod")
        output = tmp_path / "report.txt"

        result = runner.invoke(
            analyze_rod_keys, [str(tmp_path), "--output", str(output)]
        )

        assert result.exit_code == 0, result.output
        assert output.is_file()
        assert "_publ_author_name\t1" in output.read_text(encoding="utf-8")

    def test_summary_reports_key_and_file_counts(self, runner, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "a.rod")
        shutil.copy(ROD_FIXTURE, tmp_path / "b.rod")

        result = runner.invoke(analyze_rod_keys, [str(tmp_path)])

        assert result.exit_code == 0, result.output
        assert "distinct keys across 2 file(s)" in result.output

    def test_default_output_is_written_inside_rod_dir(self, runner, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "rod_file_1000679.rod")

        result = runner.invoke(analyze_rod_keys, [str(tmp_path)])

        assert result.exit_code == 0, result.output
        default_report = tmp_path / "rod_key_statistics.txt"
        assert default_report.is_file()
        assert "_publ_author_name\t1" in default_report.read_text(encoding="utf-8")

    def test_rod_dir_defaults_to_shared_batch_dir(self, runner):
        with runner.isolated_filesystem():
            batch_dir = Path(DEFAULT_ROD_BATCH_DIR)
            batch_dir.mkdir()
            shutil.copy(ROD_FIXTURE, batch_dir / "rod_file_1000679.rod")

            result = runner.invoke(analyze_rod_keys, [])

            assert result.exit_code == 0, result.output
            assert (batch_dir / "rod_key_statistics.txt").is_file()

    def test_nonexistent_rod_dir_fails(self, runner, tmp_path):
        result = runner.invoke(analyze_rod_keys, [str(tmp_path / "does_not_exist")])
        assert result.exit_code != 0
