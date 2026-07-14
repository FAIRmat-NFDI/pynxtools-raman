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
"""Entry points for Raman apps."""

try:
    from nomad.config.models.plugins import AppEntryPoint
    from nomad.config.models.ui import (
        App,
        Column,
        Menu,
        MenuItemHistogram,
        MenuItemPeriodicTable,
        MenuItemTerms,
        MenuSizeEnum,
        SearchQuantities,
    )
except ImportError as exc:
    raise ImportError(
        "Could not import nomad package. Please install the package 'nomad-lab'."
    ) from exc

schema = "pynxtools.nomad.metainfo.applications.Raman"

raman_app = AppEntryPoint(
    name="Raman App",
    description="App for Raman data.",
    app=App(
        # Label of the App
        label="Raman",
        # Path used in the URL, must be unique
        path="ramanapp",
        # Used to categorize apps in the explore menu
        category="Experiment",
        # Brief description used in the app menu
        description="A simple search app customized for Raman data.",
        # Longer description that can also use markdown
        readme="This is a simple App to support basic search for Raman based Experiment Entries.",
        # If you want to use quantities from a custom schema, you need to load
        # the search quantities from it first here. Note that you can use a glob
        # syntax to load the entire package, or just a single schema from a
        # package.
        search_quantities=SearchQuantities(
            include=[f"*#{schema}"],
        ),
        # Controls which columns are shown in the results table
        columns=[
            Column(title="Entry ID", search_quantity="entry_id", selected=True),
            Column(
                title="Material Name",
                search_quantity=f"data.sample[*].name_quantity#{schema}",
                selected=True,
            ),
            Column(
                title="Long Name",
                search_quantity=f"data.title#{schema}",
                selected=True,
            ),
        ],
        # "Space Group Number" (data.sample.space_group) and "Unit Cell
        # Volume" (data.sample.unit_cell_volume) are declared with
        # shape=["*"] (real arrays). NOMAD's dynamic search-quantity
        # registration unconditionally skips any array-shaped quantity
        # (elasticsearch_extension.create_dynamic_quantity_annotation), so
        # they cannot be used as search_quantity/quantity targets.
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # this Raman application class are included.
        filters_locked={"section_defs.definition_qualified_name": [schema]},
        # Controls the menu shown on the left
        menu=Menu(
            title="Material",
            items=[
                Menu(
                    title="Elements",
                    size=MenuSizeEnum.XXL,
                    items=[
                        MenuItemPeriodicTable(
                            search_quantity="results.material.elements",
                        ),
                        MenuItemTerms(
                            search_quantity="results.material.chemical_formula_hill",
                            width=6,
                            options=0,
                        ),
                        MenuItemTerms(
                            search_quantity="results.material.chemical_formula_iupac",
                            width=6,
                            options=0,
                        ),
                        MenuItemTerms(
                            search_quantity="results.material.chemical_formula_reduced",
                            width=6,
                            options=0,
                        ),
                        MenuItemTerms(
                            search_quantity="results.material.chemical_formula_anonymous",
                            width=6,
                            options=0,
                        ),
                        MenuItemHistogram(
                            x="results.material.n_elements",
                        ),
                    ],
                ),
                # "Space Group Number" (data.sample.space_group) is
                # array-shaped (shape=["*"]) and unsearchable, see the
                # comment near the columns above.
                Menu(
                    title="Raman Spectrometer Model",
                    items=[
                        MenuItemTerms(
                            quantity=f"data.instrument.device_information.model#{schema}#str",
                            width=10,
                            options=5,
                        ),
                    ],
                ),
                Menu(
                    title="Scattering Configuration",
                    items=[
                        MenuItemTerms(
                            quantity=f"data.instrument.scattering_configuration#{schema}#str",
                            width=10,
                            options=7,
                        ),
                    ],
                ),
                Menu(
                    title="Instruments",
                    size=MenuSizeEnum.LG,
                    items=[
                        MenuItemTerms(
                            title="Name",
                            search_quantity=f"data.instrument.name_quantity#{schema}",
                            width=12,
                            options=12,
                        ),
                        MenuItemTerms(
                            title="Short Name",
                            search_quantity=f"data.instrument.name_quantity__short_name#{schema}",
                            width=12,
                            options=12,
                        ),
                    ],
                ),
                Menu(
                    title="Samples",
                    size=MenuSizeEnum.LG,
                    items=[
                        MenuItemTerms(
                            title="Name",
                            search_quantity=f"data.sample.name_quantity#{schema}",
                            width=12,
                            options=12,
                        ),
                        # No "Sample ID" item: NXraman's Sample is the
                        # generic base_classes.Sample, which has no
                        # concretely-named identifier field (only the
                        # variadic identifierNAME, unlike NXmpes's Sample
                        # which redefines a concrete "identifier").
                    ],
                ),
                Menu(
                    title="Authors / Origin",
                    size=MenuSizeEnum.LG,
                    items=[
                        MenuItemTerms(
                            title="Entry Author",
                            search_quantity=f"data.user.name_quantity#{schema}",
                            width=12,
                            options=5,
                        ),
                        MenuItemTerms(
                            title="Upload Author",
                            search_quantity="authors.name",
                            width=12,
                            options=5,
                        ),
                        MenuItemTerms(
                            title="Affiliation",
                            search_quantity=f"data.user.affiliation#{schema}",
                            width=12,
                            options=5,
                        ),
                    ],
                ),
                MenuItemHistogram(
                    title="Start Time",
                    x=f"data.start_time#{schema}",
                    autorange=True,
                ),
                MenuItemHistogram(
                    title="Upload Creation Time",
                    x=f"upload_create_time",
                    autorange=True,
                ),
            ],
        ),
        # Controls the default dashboard shown in the search interface
        dashboard={
            "widgets": [
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.instrument.beam_TYPE.incident_wavelength#{schema}#float",
                    "title": "Incident Wavelength [nm]",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 5, "w": 8, "y": 0, "x": 0}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.instrument.beam_TYPE.average_power#{schema}#float",
                    "title": "Laser Power [mW]",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 4, "w": 8, "y": 5, "x": 0}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.instrument.optical_lens.magnification#{schema}#float",
                    "title": "Magnification",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 6, "y": 0, "x": 8}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.instrument.optical_lens.numerical_aperture#{schema}#float",
                    "title": "Numerical Aperture",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 6, "y": 3, "x": 8}
                    },
                },
                # "extent" (beam diameter) is declared with shape=["*", 2] (a
                # real array). NOMAD's dynamic search-quantity registration
                # unconditionally skips any array-shaped quantity
                # (elasticsearch_extension.create_dynamic_quantity_annotation),
                # so it cannot be used as a search_quantity/quantity target.
            ]
        },
    ),
)
