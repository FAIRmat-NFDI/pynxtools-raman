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
"""Tests for the ROD (.rod / CIF-based) reader utilities."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from pynxtools_raman.rod.rod_reader import (
    RodParser,
    _join_authors,
    _strip_cif_quotes,
    build_citation_fields,
    post_process_rod,
)

ROD_FIXTURE = Path(__file__).parent / "data" / "rod" / "rod_file_1000679.rod"


@pytest.fixture(scope="module")
def parsed_rod_data() -> dict:
    """Parse the real K-cymrite fixture once and reuse it across tests.

    Deriving expectations from the actual fixture (rather than a hand-typed
    copy of its contents) keeps the tests honest if the fixture ever changes.
    """
    parser = RodParser()
    parser.get_cif_file_content(str(ROD_FIXTURE))
    return parser.extract_keys_and_values_from_cif()


class TestRodParser:
    """RodParser.extract_keys_and_values_from_cif against a real .rod file.

    Covers the different value shapes a .rod (CIF) file can contain: plain
    scalars, quoted scalars, multi-line semicolon-delimited text, loops of
    quoted strings, and numeric loops (which get cast to float).
    """

    def test_bare_numeric_scalar_stays_a_string(self, parsed_rod_data):
        # Non-loop values are never cast to float, only loop values are.
        assert parsed_rod_data["_journal_page_first"] == "114"
        assert parsed_rod_data["_journal_year"] == "2012"

    def test_quoted_scalar_is_unquoted(self, parsed_rod_data):
        assert parsed_rod_data["_journal_name_full"] == (
            "Journal of Mineralogical and Petrological Sciences"
        )

    def test_multiline_semicolon_value_is_joined_to_one_line(self, parsed_rod_data):
        assert parsed_rod_data["_publ_section_title"] == (
            "Raman and NMR spectroscopic characterization of high-pressure "
            "K-cymrite  (KAlSi3O8 H2O) and its anhydrous form (kokchetavite) : "
            "K-cymrite"
        )

    def test_loop_of_quoted_strings_stays_quoted(self, parsed_rod_data):
        # RodParser does not strip quotes from loop values; that is left to
        # downstream consumers such as build_citation_fields/_join_authors.
        assert parsed_rod_data["_publ_author_name"] == [
            "'Kanzaki, M.'",
            "'Xue, X.'",
            "'Amalberti, J.'",
            "'Zhang, Q.'",
        ]

    def test_numeric_loop_is_parsed_as_floats(self, parsed_rod_data):
        shifts = parsed_rod_data["_raman_spectrum.raman_shift"]
        intensities = parsed_rod_data["_raman_spectrum.intensity"]

        assert shifts[:3] == [50.0, 51.262, 52.523]
        assert intensities[:3] == [429.0, 438.0, 441.0]
        assert all(isinstance(value, float) for value in shifts)
        assert len(shifts) == len(intensities) == 1159

    def test_rod_and_publication_identifiers_are_parsed(self, parsed_rod_data):
        assert parsed_rod_data["_rod_database.code"] == "1000679"
        assert parsed_rod_data["_journal_paper_doi"] == "10.2465/jmps.111020i"


class TestCifQuoteHelpers:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("'Kanzaki, M.'", "Kanzaki, M."),
            ('"Kanzaki, M."', "Kanzaki, M."),
            ("Kanzaki, M.", "Kanzaki, M."),
            ("  'Kanzaki, M.'  ", "Kanzaki, M."),
            ("", ""),
        ],
    )
    def test_strip_cif_quotes(self, raw, expected):
        assert _strip_cif_quotes(raw) == expected

    @pytest.mark.parametrize(
        "author_names, expected",
        [
            (
                ["'Kanzaki, M.'", "'Xue, X.'", "'Amalberti, J.'", "'Zhang, Q.'"],
                "Kanzaki, M.; Xue, X.; Amalberti, J.; Zhang, Q.",
            ),
            ("'Kanzaki, M.'", "Kanzaki, M."),
            (["'Kanzaki, M.'", "", None], "Kanzaki, M."),
            ([], None),
            (None, None),
            ("", None),
        ],
    )
    def test_join_authors(self, author_names, expected):
        assert _join_authors(author_names) == expected


class TestBuildCitationFields:
    def test_real_rod_entry_produces_both_citations(self, parsed_rod_data):
        fields = build_citation_fields(parsed_rod_data)

        assert fields["rod_citation_publication_author"] == (
            "Kanzaki, M.; Xue, X.; Amalberti, J.; Zhang, Q."
        )
        assert fields["rod_citation_publication_description"] == (
            "Raman and NMR spectroscopic characterization of high-pressure "
            "K-cymrite  (KAlSi3O8 H2O) and its anhydrous form (kokchetavite) : "
            "K-cymrite. Journal of Mineralogical and Petrological Sciences, "
            "114, 114-119 (2012)."
        )
        assert fields["rod_citation_rod_url"] == (
            "https://solsa.crystallography.net/rod/1000679.html"
        )
        assert (
            "Entry 1000679 in the Raman Open Database (ROD)"
            in (fields["rod_citation_rod_description"])
        )
        assert "CC0 1.0" in fields["rod_citation_rod_description"]
        assert "10.1107/S1600576719004229" in fields["rod_citation_rod_description"]

    def test_empty_input_produces_no_citations(self):
        assert build_citation_fields({}) == {}

    @pytest.mark.parametrize(
        "raman_data, expected_missing_keys",
        [
            # No publication data at all: only the (always-available) ROD
            # record citation should be built.
            (
                {"_rod_database.code": "1000679"},
                [
                    "rod_citation_publication_author",
                    "rod_citation_publication_description",
                ],
            ),
            # No ROD code: only the publication citation should be built.
            (
                {
                    "_publ_author_name": "'Kanzaki, M.'",
                    "_journal_paper_doi": "10.2465/jmps.111020i",
                },
                ["rod_citation_rod_url", "rod_citation_rod_description"],
            ),
        ],
    )
    def test_partial_input_only_builds_available_citations(
        self, raman_data, expected_missing_keys
    ):
        fields = build_citation_fields(raman_data)

        for key in expected_missing_keys:
            assert key not in fields

    def test_single_author_string_is_accepted(self):
        fields = build_citation_fields(
            {
                "_publ_author_name": "'Kanzaki, M.'",
                "_journal_paper_doi": "10.2465/jmps.111020i",
            }
        )

        assert fields["rod_citation_publication_author"] == "Kanzaki, M."

    def test_doi_alone_produces_no_description(self):
        # `doi` itself is mapped directly from `_journal_paper_doi` in
        # config_file_rod.json (not synthesized here). With no title/journal/
        # volume/pages/year to build a sentence from, no description key
        # should be added, and this must not raise.
        fields = build_citation_fields({"_journal_paper_doi": "10.2465/jmps.111020i"})

        assert fields == {}

    def test_pages_fall_back_to_whichever_page_is_available(self):
        fields = build_citation_fields(
            {
                "_publ_section_title": "Some title",
                "_journal_page_first": "114",
            }
        )
        assert "114" in fields["rod_citation_publication_description"]

        fields = build_citation_fields(
            {
                "_publ_section_title": "Some title",
                "_journal_page_last": "119",
            }
        )
        assert "119" in fields["rod_citation_publication_description"]


class TestPostProcessRod:
    """post_process_rod is bound to a RamanReader instance in reader.py; here
    it is exercised directly against a minimal stand-in object exposing the
    same `raman_data`/`missing_meta_data` attributes.
    """

    def _fake_reader(self, **raman_data) -> SimpleNamespace:
        return SimpleNamespace(
            raman_data=dict(raman_data),
            missing_meta_data=dict(raman_data),
        )

    def test_wavelength_and_resolution_are_converted_to_nm(self):
        fake = self._fake_reader(
            **{
                "_raman_measurement_device.excitation_laser_wavelength": "488",
                "_raman_measurement_device.resolution": "1",
            }
        )

        post_process_rod(fake)

        assert (
            fake.raman_data[
                "/ENTRY[entry]/INSTRUMENT[instrument]/wavelength_resolution/physical_quantity"
            ]
            == "wavelength"
        )
        assert fake.raman_data[
            "/ENTRY[entry]/INSTRUMENT[instrument]/wavelength_resolution/resolution"
        ] == pytest.approx(0.0238144)
        assert (
            fake.raman_data[
                "/ENTRY[entry]/INSTRUMENT[instrument]/wavelength_resolution/resolution/@units"
            ]
            == "nm"
        )
        assert "_raman_measurement_device.resolution" not in fake.missing_meta_data

    def test_diffraction_grating_is_converted_to_period(self):
        fake = self._fake_reader(
            **{
                "_raman_measurement_device.excitation_laser_wavelength": "488",
                "_raman_measurement_device.resolution": "1",
                "_raman_measurement_device.diffraction_grating": "1200",
            }
        )

        post_process_rod(fake)

        assert fake.raman_data[
            "/ENTRY[entry]/INSTRUMENT[instrument]/MONOCHROMATOR[monochromator]/GRATING[grating]/period"
        ] == pytest.approx(1 / 1200)

    def test_no_diffraction_grating_key_added_when_absent(self):
        fake = self._fake_reader(
            **{
                "_raman_measurement_device.excitation_laser_wavelength": "488",
                "_raman_measurement_device.resolution": "1",
            }
        )

        post_process_rod(fake)

        assert (
            "/ENTRY[entry]/INSTRUMENT[instrument]/MONOCHROMATOR[monochromator]/GRATING[grating]/period"
            not in fake.raman_data
        )
