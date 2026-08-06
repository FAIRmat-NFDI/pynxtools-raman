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
"""Tests for the ROD upload-batch pipeline (rod_batch.py)."""

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from pynxtools_raman.rod_database import DEFAULT_ROD_BATCH_DIR, rod_batch
from pynxtools_raman.rod_database.rod_batch import (
    build_rod_upload_batch,
    download_rod_files_cli,
)

ROD_FIXTURE = Path(__file__).parents[1] / "data" / "rod" / "rod_file_1000679.rod"


@pytest.fixture()
def runner():
    return CliRunner()


def test_download_and_build_upload_batch_share_the_same_option_surface():
    # Both commands are built with the same rod_batch_options decorator, so
    # they must expose (and default) the same options -- a plain download
    # followed by a batch run must not silently split files across two
    # locations or diverge in supported flags.
    download_options = {p.name for p in download_rod_files_cli.params}
    batch_options = {p.name for p in build_rod_upload_batch.params}
    assert download_options == batch_options

    def default_of(command, option_name):
        return next(p for p in command.params if p.name == option_name).default

    assert default_of(build_rod_upload_batch, "output_dir") == DEFAULT_ROD_BATCH_DIR
    assert default_of(download_rod_files_cli, "output_dir") == DEFAULT_ROD_BATCH_DIR


class TestDownloadRodFiles:
    def test_downloads_are_written_to_output_dir(self, tmp_path, monkeypatch):
        def fake_save(rod_id, output_dir=None):
            path = output_dir / f"{rod_id}.rod"
            path.write_text("fake content", encoding="utf-8")
            return path

        monkeypatch.setattr(rod_batch, "save_rod_file_from_ROD_via_API", fake_save)

        downloaded = rod_batch.download_rod_files([1, 2, 3], tmp_path)

        assert downloaded == [
            tmp_path / "1.rod",
            tmp_path / "2.rod",
            tmp_path / "3.rod",
        ]
        assert all(path.is_file() for path in downloaded)

    def test_failed_downloads_are_skipped_not_raised(self, tmp_path, monkeypatch):
        def fake_save(rod_id, output_dir=None):
            if rod_id == 2:
                return None
            path = output_dir / f"{rod_id}.rod"
            path.write_text("fake content", encoding="utf-8")
            return path

        monkeypatch.setattr(rod_batch, "save_rod_file_from_ROD_via_API", fake_save)

        downloaded = rod_batch.download_rod_files([1, 2, 3], tmp_path)

        assert downloaded == [tmp_path / "1.rod", tmp_path / "3.rod"]

    def test_creates_output_dir_if_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            rod_batch,
            "save_rod_file_from_ROD_via_API",
            lambda rod_id, output_dir=None: None,
        )
        missing_dir = tmp_path / "nested" / "dir"

        rod_batch.download_rod_files([1], missing_dir)

        assert missing_dir.is_dir()

    def test_existing_file_is_not_re_downloaded(self, tmp_path, monkeypatch):
        (tmp_path / "1.rod").write_text("already here", encoding="utf-8")
        calls = []
        monkeypatch.setattr(
            rod_batch,
            "save_rod_file_from_ROD_via_API",
            lambda rod_id, output_dir=None: calls.append(rod_id),
        )

        downloaded = rod_batch.download_rod_files([1], tmp_path)

        assert calls == []  # never called for the already-existing ID
        assert downloaded == [tmp_path / "1.rod"]
        assert (tmp_path / "1.rod").read_text(encoding="utf-8") == "already here"


class TestConvertRodFiles:
    def test_converts_real_rod_fixture_to_nxs(self, tmp_path):
        shutil.copy(ROD_FIXTURE, tmp_path / "rod_file_1000679.rod")

        converted = rod_batch.convert_rod_files(tmp_path)

        assert converted == [tmp_path / "rod_file_1000679.nxs"]
        assert converted[0].is_file()

    def test_converts_into_separate_output_dir(self, tmp_path):
        input_dir = tmp_path / "in"
        output_dir = tmp_path / "out"
        input_dir.mkdir()
        shutil.copy(ROD_FIXTURE, input_dir / "rod_file_1000679.rod")

        converted = rod_batch.convert_rod_files(input_dir, output_dir)

        assert converted == [output_dir / "rod_file_1000679.nxs"]
        assert converted[0].is_file()
        assert not (input_dir / "rod_file_1000679.nxs").exists()

    def test_no_rod_files_returns_empty_list(self, tmp_path):
        assert rod_batch.convert_rod_files(tmp_path) == []

    def test_conversion_failure_is_logged_and_skipped(self, tmp_path, caplog):
        (tmp_path / "broken.rod").write_text("not a valid cif file", encoding="utf-8")

        with caplog.at_level("ERROR"):
            converted = rod_batch.convert_rod_files(tmp_path)

        assert converted == []


class TestCollectRodIds:
    def test_collects_ids_from_args_only(self):
        assert rod_batch.collect_rod_ids(["1", "2"], None) == [1, 2]

    def test_collects_ids_from_file_only(self, tmp_path):
        ids_file = tmp_path / "ids.txt"
        ids_file.write_text("1000679\n1000680\n\n1000681\n", encoding="utf-8")

        assert rod_batch.collect_rod_ids([], ids_file) == [1000679, 1000680, 1000681]

    def test_combines_args_and_file(self, tmp_path):
        ids_file = tmp_path / "ids.txt"
        ids_file.write_text("2\n", encoding="utf-8")

        assert rod_batch.collect_rod_ids(["1"], ids_file) == [1, 2]


class TestDownloadRodFilesCli:
    """The `download` sub-command: download-only, no conversion/metadata."""

    def _fake_save(self, rod_id, output_dir=None):
        path = output_dir / f"{rod_id}.rod"
        shutil.copy(ROD_FIXTURE, path)
        return path

    def test_no_ids_given_fails_with_usage_error(self, runner, tmp_path):
        result = runner.invoke(download_rod_files_cli, ["--output-dir", str(tmp_path)])
        assert result.exit_code != 0
        assert "No ROD IDs given" in result.output

    def test_declining_confirmation_cancels(self, runner, tmp_path, monkeypatch):
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            download_rod_files_cli,
            ["1000679", "--output-dir", str(tmp_path)],
            input="n\n",
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.output
        assert not any(tmp_path.iterdir())

    def test_yes_flag_skips_confirmation_and_downloads_multiple(
        self, runner, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            download_rod_files_cli,
            ["1000679", "1000680", "--output-dir", str(tmp_path), "--yes"],
        )

        assert result.exit_code == 0, result.output
        assert "2/2 .rod file(s) present in" in result.output
        assert (tmp_path / "1000679.rod").is_file()
        assert (tmp_path / "1000680.rod").is_file()
        # download-only: no conversion, no upload metadata
        assert not (tmp_path / "1000679.nxs").exists()
        assert not (tmp_path / "nomad.json").exists()

    def test_no_prompt_when_all_files_already_present(
        self, runner, tmp_path, monkeypatch
    ):
        # A file already on disk needs no confirmation -- nothing will
        # actually be downloaded, so there's nothing to confirm. Passing no
        # `input=` at all proves this: if a prompt were shown, CliRunner
        # would hang/error waiting for stdin.
        shutil.copy(ROD_FIXTURE, tmp_path / "1000679.rod")
        monkeypatch.setattr(
            rod_batch,
            "save_rod_file_from_ROD_via_API",
            lambda rod_id, output_dir=None: (_ for _ in ()).throw(
                AssertionError("should not re-download an existing file")
            ),
        )

        result = runner.invoke(
            download_rod_files_cli, ["1000679", "--output-dir", str(tmp_path)]
        )

        assert result.exit_code == 0, result.output
        assert "Proceed?" not in result.output
        assert "1/1 .rod file(s) present in" in result.output

    def test_prompt_counts_only_the_missing_files(self, runner, tmp_path, monkeypatch):
        # 1000679 already exists, 1000680 doesn't: the prompt should ask
        # about downloading 1 file, not 2.
        shutil.copy(ROD_FIXTURE, tmp_path / "1000679.rod")
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            download_rod_files_cli,
            ["1000679", "1000680", "--output-dir", str(tmp_path)],
            input="n\n",
        )

        assert result.exit_code == 0
        assert "About to download 1 .rod file(s)" in result.output
        assert "Cancelled" in result.output

    def test_all_flag_uses_bundled_known_ids_file(self, runner, tmp_path, monkeypatch):
        known_ids_file = tmp_path / "all_known.txt"
        known_ids_file.write_text("1000679\n1000680\n", encoding="utf-8")
        monkeypatch.setattr(rod_batch, "ALL_KNOWN_ROD_IDS_FILE", known_ids_file)
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            download_rod_files_cli,
            ["--all", "--output-dir", str(tmp_path), "--yes"],
        )

        assert result.exit_code == 0, result.output
        assert (tmp_path / "1000679.rod").is_file()
        assert (tmp_path / "1000680.rod").is_file()


class TestBuildRodUploadBatchCli:
    """End-to-end test of the consolidated download -> convert -> metadata
    pipeline. The network call is faked (via the real ROD fixture content),
    everything downstream (conversion, nomad.json) runs for real.
    """

    def _fake_save(self, rod_id, output_dir=None):
        path = output_dir / f"{rod_id}.rod"
        shutil.copy(ROD_FIXTURE, path)
        return path

    def test_no_ids_given_fails_with_usage_error(self, runner, tmp_path):
        result = runner.invoke(build_rod_upload_batch, ["--output-dir", str(tmp_path)])
        assert result.exit_code != 0
        assert "No ROD IDs given" in result.output

    def test_declining_confirmation_cancels_before_converting(
        self, runner, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            build_rod_upload_batch,
            ["1000679", "--output-dir", str(tmp_path)],
            input="n\n",
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.output
        assert not any(tmp_path.iterdir())

    def test_full_pipeline_produces_rod_nxs_and_nomad_json(
        self, runner, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            build_rod_upload_batch,
            ["1000679", "--output-dir", str(tmp_path), "--yes"],
        )

        assert result.exit_code == 0, result.output
        assert (tmp_path / "1000679.rod").is_file()
        assert (tmp_path / "1000679.nxs").is_file()

        metadata = json.loads((tmp_path / "nomad.json").read_text(encoding="utf-8"))
        assert "Raman Open Database" in metadata["comment"]

    def test_ids_file_is_combined_with_positional_ids(
        self, runner, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )
        ids_file = tmp_path / "ids.txt"
        ids_file.write_text("1000679\n", encoding="utf-8")

        result = runner.invoke(
            build_rod_upload_batch,
            ["--ids-file", str(ids_file), "--output-dir", str(tmp_path), "--yes"],
        )

        assert result.exit_code == 0, result.output
        assert (tmp_path / "1000679.rod").is_file()

    def test_all_flag_uses_bundled_known_ids_file(self, runner, tmp_path, monkeypatch):
        known_ids_file = tmp_path / "all_known.txt"
        known_ids_file.write_text("1000679\n1000680\n", encoding="utf-8")
        monkeypatch.setattr(rod_batch, "ALL_KNOWN_ROD_IDS_FILE", known_ids_file)
        monkeypatch.setattr(
            rod_batch, "save_rod_file_from_ROD_via_API", self._fake_save
        )

        result = runner.invoke(
            build_rod_upload_batch,
            ["--all", "--output-dir", str(tmp_path), "--yes"],
        )

        assert result.exit_code == 0, result.output
        assert (tmp_path / "1000679.rod").is_file()
        assert (tmp_path / "1000680.rod").is_file()

    def test_all_flag_de_duplicates_against_positional_ids(
        self, runner, tmp_path, monkeypatch
    ):
        known_ids_file = tmp_path / "all_known.txt"
        known_ids_file.write_text("1000679\n", encoding="utf-8")
        monkeypatch.setattr(rod_batch, "ALL_KNOWN_ROD_IDS_FILE", known_ids_file)

        calls = []

        def fake_save(rod_id, output_dir=None):
            calls.append(rod_id)
            return self._fake_save(rod_id, output_dir=output_dir)

        monkeypatch.setattr(rod_batch, "save_rod_file_from_ROD_via_API", fake_save)

        result = runner.invoke(
            build_rod_upload_batch,
            ["1000679", "--all", "--output-dir", str(tmp_path), "--yes"],
        )

        assert result.exit_code == 0, result.output
        assert calls == [1000679]  # requested once, not twice
