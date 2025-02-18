try:
    from nomad.config.models.plugins import AppEntryPoint
except ImportError as exc:
    raise ImportError(
        "Could not import nomad package. Please install the package 'nomad-lab'."
    ) from exc

from nomad.config.models.ui import (
    App,
    Column,
    Menu,
    MenuItemHistogram,
    MenuItemPeriodicTable,
    MenuItemTerms,
    SearchQuantities,
)

schema = "pynxtools.nomad.schema.Root"

raman_app = AppEntryPoint(
    name="RamanApp",
    description="Simple Raman app.",
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
            # include=[f"data.Raman.*#{schema}"],
        ),
        # Controls which columns are shown in the results table
        columns=[
            Column(quantity="entry_id", selected=True),
            # Column(quantity=f"entry_type", selected=True),
            # Column(
            #    title="definition",
            #    quantity=f"data.*.ENTRY[*].definition__field#{schema}",
            #    selected=True,
            # ),
            Column(
                title="start_time",
                quantity=f"data.ENTRY[*].start_time__field#{schema}",
                selected=True,
            ),
            Column(
                title="title",
                quantity=f"data.ENTRY[*].title__field#{schema}",
                selected=True,
            ),
            Column(
                title="scattering_config",
                quantity=f"data.ENTRY[*].INSTRUMENT[*].scattering_configuration__field#{schema}#str",
                selected=True,
            ),
            Column(
                title="unit_cell_volume",
                quantity=f"data.ENTRY[*].SAMPLE[*].unit_cell_volume__field#{schema}",
                selected=True,
            ),
            # Only 311 of 1131 ROD entries have this field...
            # Column(
            #    title="physical_form",
            #    quantity=f"data.*.ENTRY[*].SAMPLE[*].physical_form__field#{schema}",
            #    selected=True,
            # ),
            # add this:
            # exfitation wavelength --> need deeper search for quantities in nexus
        ],
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        # filters_locked={"section_defs.definition_qualified_name": [schema]},
        filters_locked={f"data.ENTRY.definition__field#{schema}": ["NXraman"]},
        # Controls the menu shown on the left
        menu=Menu(
            title="Material",
            items=[
                Menu(
                    title="elements",
                    items=[
                        MenuItemPeriodicTable(
                            quantity="results.material.elements",
                        ),
                        MenuItemTerms(
                            quantity="results.material.chemical_formula_hill",
                            width=6,
                            options=0,
                        ),
                        MenuItemTerms(
                            quantity="results.material.chemical_formula_iupac",
                            width=6,
                            options=0,
                        ),
                        MenuItemHistogram(
                            x="results.material.n_elements",
                        ),
                    ],
                )
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
                    "scale": "linear",
                    "quantity": f"data.ENTRY.start_time__field#{schema}",
                    "title": "Start Time",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 4, "w": 12, "y": 0, "x": 0}
                    },
                },
                {
                    "type": "terms",
                    "show_input": False,
                    "scale": "linear",
                    "quantity": f"data.ENTRY.INSTRUMENT.scattering_configuration__field#{schema}#str",
                    "title": "Scattering Config2",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 4, "w": 4, "y": 0, "x": 12}
                    },
                },
                {
                    "type": "terms",
                    "show_input": False,
                    "scale": "linear",
                    "quantity": f"data.ENTRY.raman_experiment_type__field#{schema}#str",
                    "title": "Raman Type",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 4, "w": 8, "y": 0, "x": 16}
                    },
                },
                {
                    "type": "periodic_table",
                    "scale": "linear",
                    "quantity": f"results.material.elements",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 6, "w": 12, "y": 4, "x": 0}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "linear",
                    "quantity": f"data.ENTRY.SAMPLE.unit_cell_volume__field#{schema}",  # data.Raman.ENTRY.SAMPLE.unit_cell_volume__field#pynxtools.nomad.schema.NeXus
                    "title": "Unit Cell Volume",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 6, "w": 12, "y": 4, "x": 12}
                    },
                },
            ]
        },
    ),
)
