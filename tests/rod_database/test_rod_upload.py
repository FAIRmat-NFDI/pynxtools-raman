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


def test_upload_batch_sets_upload_name_if_given(tmp_path, monkeypatch):
    fake = FakeUploads()
    monkeypatch.setattr(rod_upload, "_import_nomad_utility_workflows", lambda: fake)

    rod_upload.upload_batch(tmp_path / "batch.zip", upload_name="ROD pilot batch")

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
