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
"""Tests for the NOMAD app."""

import pytest

try:
    import nomad  # noqa: F401
except ImportError:
    pytest.skip(
        "Skipping NOMAD app tests because nomad-lab is not installed",
        allow_module_level=True,
    )

# this will raise an exception if pydantic model validation fails for the app
from pynxtools_raman.nomad.apps import raman_app, schema  # noqa: PLC0415


def test_raman_app_basic_properties():
    """Verify basic metadata of the Raman app."""
    app = raman_app.app

    assert app.label == "Raman"
    assert app.path == "ramanapp"
    assert app.category == "Experiment"


def test_raman_app_schema():
    """App must reference the correct Raman class."""
    assert schema == "pynxtools.nomad.metainfo.applications.Raman"
    filters = raman_app.app.filters_locked
    assert "section_defs.definition_qualified_name" in filters
    assert filters["section_defs.definition_qualified_name"] == [schema]


def test_raman_app_locked_filters():
    """Ensure required locked filters are defined and well-formed."""
    app = raman_app.app

    assert "section_defs.definition_qualified_name" in app.filters_locked
    assert isinstance(
        app.filters_locked["section_defs.definition_qualified_name"], list
    )
    assert len(app.filters_locked["section_defs.definition_qualified_name"]) == 1


def test_raman_app_columns():
    """Check that representative result columns are configured correctly."""
    app = raman_app.app

    material_column = next(col for col in app.columns if col.title == "Material Name")
    assert material_column.selected is True
    assert "data.sample" in material_column.search_quantity


def test_raman_app_menu_contains_elements_section():
    """Validate presence and structure of the Elements menu section."""
    app = raman_app.app

    elements_menu = next(item for item in app.menu.items if item.title == "Elements")

    assert elements_menu.size.name == "XXL"
    assert any(
        item.__class__.__name__ == "MenuItemPeriodicTable"
        for item in elements_menu.items
    )


def test_raman_app_menu_contains_instruments_section():
    """Validate presence and structure of the Instruments menu section."""
    app = raman_app.app

    instruments_menu = next(
        item for item in app.menu.items if item.title == "Instruments"
    )

    assert instruments_menu.size.name == "LG"
    titles = [item.title for item in instruments_menu.items]
    assert "Name" in titles
    assert "Short Name" in titles


def test_raman_app_menu_contains_scattering_configuration_section():
    """Validate presence of the Scattering Configuration menu section."""
    app = raman_app.app

    scattering_menu = next(
        item for item in app.menu.items if item.title == "Scattering Configuration"
    )

    assert len(scattering_menu.items) == 1


def test_raman_app_dashboard_widgets():
    """Ensure the dashboard contains the expected histogram widgets."""
    dashboard = raman_app.app.dashboard

    assert len(dashboard.widgets) > 0

    titles = [w.title for w in dashboard.widgets]
    assert "Incident Wavelength [nm]" in titles
    assert "Laser Power [mW]" in titles

    wavelength = next(
        w for w in dashboard.widgets if w.title == "Incident Wavelength [nm]"
    )
    assert wavelength.type == "histogram"
    assert wavelength.layout
    assert "incident_wavelength" in wavelength.x.search_quantity
