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
"""Tests for the NOMAD upload step (rod_upload.py).

nomad_utility_workflows is never actually imported here: rod_upload.py
imports it lazily through _import_nomad_utility_workflows(), which these
tests replace with a fake, so no NOMAD credentials or network access are
needed to run them.
"""

import zipfile
from pathlib import Path
from types import SimpleNamespace

import click
import pytest

from pynxtools_raman.rod_database import rod_upload


def test_zip_upload_batch_writes_files_at_archive_root(tmp_path):
    batch_dir = tmp_path / "batch"
    batch_dir.mkdir()
    (batch_dir / "1000679.nxs").write_text("fake nxs content")
    (batch_dir / "nomad.json").write_text("{}")

    zip_path = rod_upload.zip_upload_batch(batch_dir)

    assert zip_path == batch_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path) as zf:
        assert sorted(zf.namelist()) == ["1000679.nxs", "nomad.json"]


def test_zip_upload_batch_honors_explicit_zip_path(tmp_path):
    batch_dir = tmp_path / "batch"
    batch_dir.mkdir()
    (batch_dir / "a.nxs").write_text("x")
    custom_zip = tmp_path / "custom_name.zip"

    zip_path = rod_upload.zip_upload_batch(batch_dir, zip_path=custom_zip)

    assert zip_path == custom_zip
    assert zip_path.is_file()


class TestBatchFiles:
    def test_splits_into_groups_of_at_most_batch_size(self):
        files = [Path(f"{i}.nxs") for i in range(5)]

        batches = rod_upload.batch_files(files, batch_size=2)

        assert batches == [files[0:2], files[2:4], files[4:5]]

    def test_exact_multiple_produces_evenly_sized_batches(self):
        files = [Path(f"{i}.nxs") for i in range(4)]

        batches = rod_upload.batch_files(files, batch_size=2)

        assert [len(batch) for batch in batches] == [2, 2]

    def test_batch_size_larger_than_input_produces_one_batch(self):
        files = [Path(f"{i}.nxs") for i in range(3)]

        batches = rod_upload.batch_files(files, batch_size=10)

        assert batches == [files]

    def test_empty_input_produces_no_batches(self):
        assert rod_upload.batch_files([], batch_size=5) == []


class TestStageBatch:
    def test_populates_batch_dir_and_zips_cleanly(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        nxs_files = []
        for name in ("1000679.nxs", "1000680.nxs", "1000681.nxs"):
            path = source_dir / name
            path.write_text(f"fake content for {name}")
            nxs_files.append(path)
        nomad_json_path = source_dir / "nomad.json"
        nomad_json_path.write_text('{"comment": "..."}')

        batch_dir = tmp_path / "batch_001"
        # Only stage a subset (the first two) -- this is the whole point of
        # batching: not every file in source_dir goes into every batch.
        rod_upload.stage_batch(nxs_files[:2], nomad_json_path, batch_dir)

        assert sorted(p.name for p in batch_dir.iterdir()) == [
            "1000679.nxs",
            "1000680.nxs",
            "README.md",
            "nomad.json",
        ]
        # The staged files are independent copies, not the batch's only
        # reference to the originals.
        assert (batch_dir / "1000679.nxs").read_text() == "fake content for 1000679.nxs"

        # zip_upload_batch (unchanged, already used for the non-batched
        # case) must be able to consume a staged batch directory as-is.
        zip_path = rod_upload.zip_upload_batch(batch_dir)
        with zipfile.ZipFile(zip_path) as zf:
            assert sorted(zf.namelist()) == [
                "1000679.nxs",
                "1000680.nxs",
                "README.md",
                "nomad.json",
            ]

    def test_readme_lists_only_this_batch_files(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        a = source_dir / "a.nxs"
        a.write_text("a")
        b = source_dir / "b.nxs"
        b.write_text("b")
        nomad_json_path = source_dir / "nomad.json"
        nomad_json_path.write_text("{}")

        batch_dir = tmp_path / "batch_001"
        rod_upload.stage_batch([a], nomad_json_path, batch_dir)

        readme = (batch_dir / "README.md").read_text(encoding="utf-8")
        assert "a.nxs" in readme
        assert "b.nxs" not in readme


class FakeUploads:
    """Stand-in for nomad_utility_workflows.utils.uploads."""

    def __init__(self):
        self.upload_calls = []
        self.metadata_calls = []
        self.publish_calls = []
        self.statuses = iter([])

    def upload_files_to_nomad(self, filename, url=None, **kwargs):
        self.upload_calls.append((filename, url))
        return "upload123"

    def edit_upload_metadata(self, upload_id, upload_metadata=None, url=None, **kwargs):
        self.metadata_calls.append((upload_id, upload_metadata, url))
        return {}

    def get_upload_by_id(self, upload_id, url=None, **kwargs):
        return next(self.statuses)

    def publish_upload(self, upload_id, url=None, **kwargs):
        self.publish_calls.append((upload_id, url))
        return {}


def test_upload_batch_uploads_and_returns_upload_id(tmp_path, monkeypatch):
    fake = FakeUploads()
    monkeypatch.setattr(rod_upload, "_import_nomad_utility_workflows", lambda: fake)

    upload_id = rod_upload.upload_batch(tmp_path / "batch.zip")

    assert upload_id == "upload123"
    assert fake.upload_calls == [(str(tmp_path / "batch.zip"), None)]
    assert fake.metadata_calls == []


def test_set_upload_name_calls_edit_upload_metadata(monkeypatch):
    fake = FakeUploads()
    monkeypatch.setattr(rod_upload, "_import_nomad_utility_workflows", lambda: fake)

    rod_upload.set_upload_name("upload123", "ROD pilot batch")

    assert fake.metadata_calls == [
        ("upload123", {"upload_name": "ROD pilot batch"}, None)
    ]


def test_upload_batch_raises_usage_error_when_client_cannot_be_imported(monkeypatch):
    def raise_usage_error():
        raise click.UsageError("nope")

    monkeypatch.setattr(
        rod_upload, "_import_nomad_utility_workflows", raise_usage_error
    )

    with pytest.raises(click.UsageError):
        rod_upload.upload_batch(Path("batch.zip"))


def test_wait_for_processing_polls_until_not_running(monkeypatch):
    fake = FakeUploads()
    fake.statuses = iter(
        [
            SimpleNamespace(process_running=True, process_status="RUNNING"),
            SimpleNamespace(process_running=True, process_status="RUNNING"),
            SimpleNamespace(process_running=False, process_status="SUCCESS"),
        ]
    )
    monkeypatch.setattr(rod_upload, "_import_nomad_utility_workflows", lambda: fake)
    monkeypatch.setattr(rod_upload.time, "sleep", lambda _: None)

    result = rod_upload.wait_for_processing("upload123")

    assert result.process_status == "SUCCESS"


def test_publish_batch_upload_calls_publish(monkeypatch):
    fake = FakeUploads()
    monkeypatch.setattr(rod_upload, "_import_nomad_utility_workflows", lambda: fake)

    rod_upload.publish_batch_upload("upload123")

    assert fake.publish_calls == [("upload123", None)]
