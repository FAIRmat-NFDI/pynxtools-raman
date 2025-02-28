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
            Column(
                title="Material Name",
                quantity=f"data.ENTRY[*].SAMPLE[*].name__field#{schema}",
                selected=True,
            ),
            Column(
                title="Space Group Number",
                quantity=f"data.ENTRY[*].SAMPLE[*].space_group__field#{schema}#str",
                selected=True,
            ),
            # Column(
            #    title="Temperature",
            #    quantity=f"data.ENTRY[*].SAMPLE[*].ENVIRONMENT[1].SENSOR[*].value__field#{schema}",
            #    selected=True,
            # ),
            Column(
                title="Unit Cell Volume",
                quantity=f"data.ENTRY[*].SAMPLE[*].unit_cell_volume__field#{schema}",
                selected=True,
            ),
            Column(
                title="Long Name",
                quantity=f"data.ENTRY[*].title__field#{schema}",
                selected=True,
            ),
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
                    title="Elements",
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
                ),
                Menu(
                    title="Space Group Number",
                    items=[
                        MenuItemTerms(
                            quantity=f"data.ENTRY.SAMPLE.space_group__field#{schema}#str",
                            width=10,
                            options=10,
                        ),
                    ],
                ),
                Menu(
                    title="Raman Spectrometer Model",
                    items=[
                        MenuItemTerms(
                            quantity=f"data.ENTRY.INSTRUMENT.device_information.model__field#{schema}#str",
                            width=10,
                            options=5,
                        ),
                    ],
                ),
                Menu(
                    title="Scattering Configuration",
                    items=[
                        MenuItemTerms(
                            quantity=f"data.ENTRY.INSTRUMENT.scattering_configuration__field#{schema}#str",
                            width=10,
                            options=7,
                        ),
                    ],
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
                    "quantity": f"data.ENTRY.INSTRUMENT.beam_incident.wavelength__field#{schema}#float",
                    "title": "Incident Wavelength [nm]",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 8, "y": 0, "x": 0}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.ENTRY.INSTRUMENT.beam_incident.average_power__field#{schema}#float",
                    "title": "Laser Power [mW]",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 8, "y": 3, "x": 0}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.ENTRY.INSTRUMENT.LENS_OPT.magnification__field#{schema}#float",
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
                    "quantity": f"data.ENTRY.INSTRUMENT.LENS_OPT.numerical_aperture__field#{schema}#float",
                    "title": "Numerical Aperture",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 6, "y": 3, "x": 8}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.ENTRY.INSTRUMENT.beam_incident.extent__field#{schema}#float",
                    "title": "Beam Diameter [µm]",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 6, "y": 6, "x": 8}
                    },
                },
                {
                    "type": "histogram",
                    "show_input": False,
                    "autorange": True,
                    "nbins": 30,
                    "scale": "log",
                    "quantity": f"data.ENTRY.SAMPLE.temperature_env.SENSOR.value__field#{schema}#float",
                    "title": "Sample Temperature [K]",
                    "layout": {
                        "lg": {"minH": 3, "minW": 3, "h": 3, "w": 8, "y": 6, "x": 0}
                    },
                },



            ]
        },
    ),
)
